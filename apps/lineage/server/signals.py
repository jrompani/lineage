from utils.dynamic_import import get_query_class
LineageAccount = get_query_class("LineageAccount")

try:
    LineageAccount.ensure_columns()
except:
    pass
