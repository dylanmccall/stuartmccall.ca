from django.conf import settings

def smc_settings(request):
    return {'smc_google_analytics_id': getattr(settings, 'SMC_GOOGLE_ANALYTICS_ID', None)}
