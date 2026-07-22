from django.core.mail import send_mail
from django.conf import settings
from .models import SafeTrip

def notify_guardians(safe_trip: SafeTrip, event_description: str):
    """
    Busca todos los guardianes del usuario y les envía una notificación.
    Actualmente configurado para enviar correos si el guardián tiene un email.
    """
    user = safe_trip.user
    guardians = user.guardians.filter(is_active=True)
    
    # Preparar listas de contactos
    emails_to_notify = []
    
    for guardian in guardians:
        if guardian.email:
            emails_to_notify.append(guardian.email)
            
        if emails_to_notify:
            subject = f"SafeFlow: Actualización del viaje de {user.first_name or user.username}"
            
            # Mensaje en texto plano (fallback)
            text_message = (
                f"Hola,\n\n"
                f"Este es un aviso automático de SafeFlow.\n"
                f"El usuario {user.first_name or user.username} ha tenido la siguiente actualización en su viaje:\n\n"
                f"EVENTO: {event_description}\n"
                f"ESTADO DEL VIAJE: {safe_trip.get_status_display()}\n\n"
                f"Para ver el progreso en vivo, por favor revisa la aplicación.\n\n"
                f"Saludos,\nEl equipo de Palenque Go"
            )
            
            # Mensaje HTML (Diseño bonito)
            html_message = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #059669; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">🛡️ SafeFlow de Palenque Go</h1>
                </div>
                <div style="padding: 20px; background-color: #ffffff; color: #333333;">
                    <p style="font-size: 16px;">Hola,</p>
                    <p style="font-size: 16px;">Este es un aviso automático de seguridad. El pasajero <strong>{user.first_name or user.username}</strong> ha actualizado su ubicación:</p>
                    
                    <div style="background-color: #f3f4f6; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0; font-size: 18px; font-weight: bold; color: #111827;">📍 {event_description}</p>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #6b7280;">Estado: {safe_trip.get_status_display()}</p>
                    </div>
                    
                    <p style="font-size: 14px; color: #6b7280;">Si tienes alguna preocupación, por favor contacta al usuario directamente.</p>
                </div>
                <div style="background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #e0e0e0;">
                    <p style="margin: 0;">© 2026 Palenque Go. Todos los derechos reservados.</p>
                </div>
            </div>
            """
            
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    emails_to_notify,
                    fail_silently=False,
                    html_message=html_message
                )
                print(f"[SafeFlow] Correo enviado a {len(emails_to_notify)} guardianes.")
            except Exception as e:
                print(f"[SafeFlow ERROR] No se pudo enviar el correo: {e}")

        # Enviar también por Telegram si el guardián lo tiene configurado
        if guardian.telegram_chat_id:
            send_telegram_message(guardian.telegram_chat_id, f"🛡️ *SafeFlow de Palenque Go*\n\nHola, {guardian.name}. El usuario {user.first_name or user.username} ha tenido la siguiente actualización en su viaje:\n\n📍 *{event_description}*\nEstado: {safe_trip.get_status_display()}\n\n_Para ver el progreso en vivo, por favor revisa la aplicación._")

def send_telegram_message(chat_id, text):
    import requests
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        print("[SafeFlow ERROR] TELEGRAM_BOT_TOKEN no configurado en settings.")
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[SafeFlow ERROR] Error al enviar Telegram a {chat_id}: {e}")
