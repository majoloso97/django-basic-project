def universal_notify(*args, **kwargs):
    not_type = kwargs.get('notification_type', '')
    msg = f'Notification {not_type} sent'
    print(msg)
