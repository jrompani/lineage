from django.shortcuts import render, get_object_or_404, redirect
from apps.main.home.decorator import conditional_otp_required
from django.contrib import messages
from django.db import transaction
from .models import ShopItem, ShopPackage, Cart, CartItem, CartPackage, PromotionCode, ShopPurchase
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory
from apps.lineage.wallet.models import Wallet
from django.core.paginator import Paginator

from utils.services import verificar_conquistas
from apps.main.home.models import PerfilGamer

from utils.dynamic_import import get_query_class
LineageServices = get_query_class("LineageServices")


@conditional_otp_required
def shop_home(request):
    item_list = ShopItem.objects.filter(ativo=True)
    package_list = ShopPackage.objects.filter(ativo=True)

    item_paginator = Paginator(item_list, 6)  # 6 por página
    package_paginator = Paginator(package_list, 6)

    item_page = request.GET.get('items_page')
    package_page = request.GET.get('packages_page')

    items = item_paginator.get_page(item_page)
    packages = package_paginator.get_page(package_page)

    return render(request, 'shop/home.html', {
        'items': items,
        'packages': packages
    })


@conditional_otp_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    # Lista os personagens da conta
    try:
        personagens = LineageServices.find_chars(request.user.username)
    except:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')
    return render(request, 'shop/cart.html', {'cart': cart, "personagens": personagens})


@conditional_otp_required
def add_item_to_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(ShopItem, id=item_id, ativo=True)
    
    quantidade = int(request.POST.get('quantidade', 1))
    if quantidade < 1:
        messages.error(request, "A quantidade deve ser maior que zero.")
        return redirect('shop:shop_home')
        
    if quantidade > 99:  # Limite máximo por item
        messages.error(request, "Quantidade máxima excedida.")
        return redirect('shop:shop_home')
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantidade += quantidade
        if cart_item.quantidade > 99:
            messages.error(request, "Quantidade máxima no carrinho excedida.")
            return redirect('shop:shop_home')
    else:
        cart_item.quantidade = quantidade
    cart_item.save()
    
    messages.success(request, f"{item.nome} adicionado ao carrinho.")
    return redirect('shop:shop_home')


@conditional_otp_required
def add_package_to_cart(request, package_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    pacote = get_object_or_404(ShopPackage, id=package_id, ativo=True)
    cart_package, created = CartPackage.objects.get_or_create(cart=cart, pacote=pacote)
    if not created:
        cart_package.quantidade += 1
    cart_package.save()
    messages.success(request, f"Pacote {pacote.nome} adicionado ao carrinho.")
    return redirect('shop:shop_home')


@conditional_otp_required
def apply_promo_code(request):
    if request.method == "POST":
        code = request.POST.get("promo_code")
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            promo = PromotionCode.objects.get(codigo=code, ativo=True)
            if not promo.is_valido():
                messages.error(request, "Código expirado ou inválido.")
            else:
                cart.promocao_aplicada = promo
                cart.save()
                messages.success(request, f"Cupom {promo.codigo} aplicado!")
        except PromotionCode.DoesNotExist:
            messages.error(request, "Cupom não encontrado.")
    return redirect('shop:view_cart')


@conditional_otp_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    wallet, _ = Wallet.objects.get_or_create(usuario=request.user)

    total = cart.calcular_total()

    if wallet.saldo < total:
        messages.error(request, "Saldo insuficiente na carteira.")
        return redirect('shop:view_cart')

    personagem = request.POST.get('character_name')
    if not personagem or len(personagem.strip()) < 3:
        messages.error(request, "Informe um nome de personagem válido para entrega (mínimo 3 caracteres).")
        return redirect('shop:view_cart')
    
    # Verificar se o personagem existe no inventário do usuário
    if not Inventory.objects.filter(user=request.user, character_name=personagem).exists():
        messages.error(request, 'Este personagem não pertence a você.')
        return redirect('shop:view_cart')

    if not cart.cartitem_set.exists() and not cart.cartpackage_set.exists():
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('shop:view_cart')

    try:
        with transaction.atomic():
            # Descontar do saldo
            aplicar_transacao(wallet, 'SAIDA', total, descricao="Compra no Shop")

            # Enviar itens e pacotes para o inventário
            inventory, _ = Inventory.objects.get_or_create(
                user=request.user,
                account_name=request.user.username,
                character_name=personagem
            )

            # Adicionar os itens do carrinho no inventário
            for cart_item in cart.cartitem_set.all():
                quantidade_total = cart_item.quantidade * cart_item.item.quantidade

                existing_item = InventoryItem.objects.filter(
                    inventory=inventory,
                    item_id=cart_item.item.item_id
                ).first()

                if existing_item:
                    existing_item.quantity += quantidade_total
                    existing_item.save()
                else:
                    InventoryItem.objects.create(
                        inventory=inventory,
                        item_id=cart_item.item.item_id,
                        item_name=cart_item.item.nome,
                        quantity=quantidade_total
                    )

            # Adicionar os itens dos pacotes no inventário
            for cart_package in cart.cartpackage_set.all():
                for pacote_item in cart_package.pacote.shoppackageitem_set.all():
                    quantidade_total = pacote_item.quantidade * pacote_item.item.quantidade * cart_package.quantidade

                    existing_item = InventoryItem.objects.filter(
                        inventory=inventory,
                        item_id=pacote_item.item.item_id
                    ).first()

                    if existing_item:
                        existing_item.quantity += quantidade_total
                        existing_item.save()
                    else:
                        InventoryItem.objects.create(
                            inventory=inventory,
                            item_id=pacote_item.item.item_id,
                            item_name=pacote_item.item.nome,
                            quantity=quantidade_total
                        )

            # Registrar a compra
            ShopPurchase.objects.create(
                user=request.user,
                character_name=personagem,
                total_pago=total,
                promocao_aplicada=cart.promocao_aplicada
            )

            cart.limpar()
            messages.success(request, "Compra realizada com sucesso! Itens enviados para o inventário.")

            perfil = PerfilGamer.objects.get(user=request.user)
            perfil.adicionar_xp(40)
            verificar_conquistas(request.user, request=request)

            return redirect('shop:purchase_history')

    except Exception as e:
        messages.error(request, "Erro ao processar a compra. Por favor, tente novamente.")
        return redirect('shop:view_cart')


@conditional_otp_required
def purchase_history(request):
    purchases = ShopPurchase.objects.filter(user=request.user).order_by('-data_compra')
    return render(request, 'shop/purchases.html', {'purchases': purchases})


@conditional_otp_required
def clear_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.limpar()
    messages.success(request, "Carrinho esvaziado com sucesso.")
    return redirect('shop:view_cart')


@conditional_otp_required
def remove_cart_item(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
        cart_item.delete()
        messages.success(request, f"{cart_item.item.nome} removido do carrinho.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item não encontrado no carrinho.")
    return redirect('shop:view_cart')


@conditional_otp_required
def remove_cart_package(request, package_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_package = CartPackage.objects.get(cart=cart, pacote_id=package_id)
        cart_package.delete()
        messages.success(request, f"Pacote {cart_package.pacote.nome} removido do carrinho.")
    except CartPackage.DoesNotExist:
        messages.error(request, "Pacote não encontrado no carrinho.")
    return redirect('shop:view_cart')
