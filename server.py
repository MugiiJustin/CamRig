import ssl
import cv2
import pigpio
from aiohttp import web

pi = pigpio.pi()
cam = cv2.VideoCapture(0)


async def index(request):
    return web.FileResponse('index.html')


async def quest(request):
    return web.FileResponse('quest.html')


async def yaw(request):
    a = max(-90, min(90, float(request.match_info['v'])))
    pi.set_servo_pulsewidth(13, 1500 + a * 2000 / 180)
    return web.Response()


async def frame(request):
    img = cam.read()[1]
    _, buf = cv2.imencode('.jpg', img)
    try:
        small = cv2.resize(img, (480, 320))
        with open('/dev/fb1', 'wb') as lcd:
            lcd.write(cv2.cvtColor(small, cv2.COLOR_BGR2BGR565).tobytes())
    except (OSError, cv2.error):
        pass
    return web.Response(body=buf.tobytes(), content_type='image/jpeg')


app = web.Application()
app.add_routes([web.get('/', index), web.get('/quest', quest), web.get('/yaw/{v}', yaw), web.get('/frame.jpg', frame)])

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('cert.pem', 'key.pem')
web.run_app(app, ssl_context=ctx, port=8443)

# one-time cert:
# openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj /CN=pi
# servo signal wire on GPIO 13 (pin 33); run: sudo pigpiod && python3 server.py
# Quest browser: https://<pi-ip>:8443/quest -> accept warning -> Enter VR
# Phone: https://<pi-ip>:8443
