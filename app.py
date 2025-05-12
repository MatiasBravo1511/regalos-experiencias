from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta, timezone
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import chardet
import time
import json
 
    
# Funcion para leer regalos
def cargar_regalos():
    global regalos
    try:
        with open("regalos.json", "r", encoding="utf-8") as f:
            regalos_json = json.load(f)
            regalos = []
            for r in regalos_json:
                r["fecha"] = datetime.fromisoformat(r["fecha"])
                regalos.append(r)
    except FileNotFoundError:
        regalos = []

cargar_regalos()

# Configuración de Gmail IMAP
EMAIL_USER = "maticoteregalos@gmail.com"
EMAIL_PASS = "qlhx kwrt kwxx pgap"
IMAP_SERVER = "imap.gmail.com"

def leer_emails_y_confirmar(callback_confirmar):
    cargar_regalos()
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()

        for eid in email_ids:
            res, msg_data = mail.fetch(eid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")

                    # Revisa si el mensaje tiene cuerpo de texto
                    cuerpo = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_dispo = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_dispo:
                                try:
                                    raw_bytes = part.get_payload(decode=True)
                                    cuerpo = raw_bytes.decode("utf-8")
                                except UnicodeDecodeError:
                                    resultado = chardet.detect(raw_bytes)
                                    encoding = resultado["encoding"] or "latin-1"
                                    cuerpo = raw_bytes.decode(encoding, errors="replace")
                                break
                    else:
                        try:
                            raw_bytes = msg.get_payload(decode=True)
                            cuerpo = raw_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            resultado = chardet.detect(raw_bytes)
                            encoding = resultado["encoding"] or "latin-1"
                            cuerpo = raw_bytes.decode(encoding, errors="replace")

                    print("📨 Asunto:", subject, flush=True)
                    print("🧾 Cuerpo:", cuerpo[:300], flush=True)  # muestra los primeros 300 caracteres

                    # FILTRO: si contiene "Slach" o un nombre conocido
                    if "slach" in subject.lower() or "slach" in cuerpo.lower():
                        print(f"📥 Detectado correo relacionado a pago: {subject}", flush=True)
                        callback_confirmar(subject + cuerpo)

        for eid in email_ids:
            mail.store(eid, '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.logout()
    except Exception as e:
        print("❌ Error al leer correos:", e, flush=True)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para mantener la sesión segura

experiencias_regaladas = set()

@app.route('/')
def index():
    cargar_regalos()  # 🔄 lee el archivo .json cada vez que se entra

    # Obtener nombres de experiencias ya confirmadas
    experiencias_confirmadas = {
        exp["nombre"]
        for r in regalos if r.get("confirmado")
        for exp in r["experiencias"]
    }
    
    experiencias = [
        {
            "nombre": "Cena Romántica en Hotel Antumalal",
            "precio": 90000,
            "descripcion": "Comida rica en el hotel de la ceremonia de matrimonio.",
            "imagen": "img/cena-antumalal.jpg"
        },
        {
            "nombre": "Masa Madre de 100 años",
            "precio": 50000,
            "descripcion": "Después de mil intentos, necesitamos un milagro. Para que al Mati por fin le quede bien el pan.",
            "imagen": "img/masa-madre.jpg"
        },
        {
            "nombre": "Ficus Lyrata de 2 metros",
            "precio": 150000,
            "descripcion": "Porque la tercera es la vencida (que no se muera esta vez por favor), para decorar nuestra casa en el bosque.",
            "imagen": "img/ficus-lyrata.jpg"
        },
        {
            "nombre": "Rafting en el Trancura",
            "precio": 50000,
            "descripcion": "Un poco de adrenalina para alivinar el estrés de esta vida en el sur.",
            "imagen": "img/rafting.jpg"
        },
        {
            "nombre": "Viaje ida y vuelta a Santiago para dos",
            "precio": 150000,
            "descripcion": "Para poder visitarlos.",
            "imagen": "img/viaje-santiago.jpg"
        },
        {
            "nombre": "Viaje de Cicloturismo para dos por el sur de Chile",
            "precio": 170000,
            "descripcion": "Para poder revivir uno de nuestros primeros (y más sufridos) viajes por Chile.",
            "imagen": "img/cicloturismo.jpg"
        },
        {
            "nombre": "Curso de Compostaje",
            "precio": 80000,
            "descripcion": "Para hacer compost para nuestras plantitas sureñas.",
            "imagen": "img/compostaje.jpg"
        },
        {
            "nombre": "Invernadero para el bosque",
            "precio": 100000,
            "descripcion": "Para alojar nuestras plantitas sureñas.",
            "imagen": "img/invernadero.jpg"
        },
        {
            "nombre": "Casa propia para los gatos",
            "precio": 80000,
            "descripcion": "Ya están en edad de independizarse.",
            "imagen": "img/casa-gatos.jpg"
        },
        {
            "nombre": "Expedición para sacar el salmón Chinook",
            "precio": 100000,
            "descripcion": "Ya que siempre sacamos puros llaveros.",
            "imagen": "img/chinook.jpg"
        },
        {
            "nombre": "Espada Master Sword de Zelda",
            "precio": 50000,
            "descripcion": "Es hora de salvar a la princesa Zelda.",
            "imagen": "img/master-sword.jpg"
        },
        {
            "nombre": "Circuito O de las Tores del Paine para dos",
            "precio": 100000,
            "descripcion": "Ayúdanos a cumplir uno de nuestros sueños en uno de los lugares más lindos de Chile.",
            "imagen": "img/torres-del-paine.jpg"
        },
        {
            "nombre": "Entrada a carrera de ultraciclismo Brevet",
            "precio": 50000,
            "descripcion": "Para continuar con este sufrido hobbie.",
            "imagen": "img/brevet.jpg"
        },
        {
            "nombre": "Meet & Greet con Erlend Øye",
            "precio": 100000,
            "descripcion": "Spoiler: van a escuchar mucho de él en nuestra ceremonia.",
            "imagen": "img/erlend-oye.jpg"
        },
        {
            "nombre": "Concierto privado de Cristóbal Briceño",
            "precio": 80000,
            "descripcion": "Nuestro funado favorito.",
            "imagen": "img/briceño.jpg"
        },
        {
            "nombre": "Curso de barista",
            "precio": 50000,
            "descripcion": "Para que puedan deleitarse con ricos cafés cada vez que vengan a Pucón.",
            "imagen": "img/barista.jpg"
        },
        {
            "nombre": "Aeropress",
            "precio": 50000,
            "descripcion": "Ayúdanos a seguir alimentando esta adicción al café.",
            "imagen": "img/aeropress.jpg"
        },
        {
            "nombre": "Saco de café de grano",
            "precio": 50000,
            "descripcion": "El buen café viene desde su origen y tueste.",
            "imagen": "img/cafe.jpg"
        },
        {
            "nombre": "Revelado de fotos infinito",
            "precio": 100000,
            "descripcion": "Para que la Cote ya no dependa de la tienda Migo.",
            "imagen": "img/revelado.jpg"
        },
        {
            "nombre": "Compra de 100 kinos para ganarse el Chao Jefe",
            "precio": 50000,
            "descripcion": "Justo y necesario.",
            "imagen": "img/chao-jefe.jpeg"
        },
        {
            "nombre": "Membresía anual de Mubi",
            "precio": 50000,
            "descripcion": "Para que la Cote se siga dando color.",
            "imagen": "img/mubi.jpg"
        },
        {
            "nombre": "Cena de lujo para Olivia, Mikasa, Elvis y Miso",
            "precio": 100000,
            "descripcion": "Una cena de lujo para nuestros hijos que incluirá Salmón, Atún, Pollo sazonado al Catnip con relleno de Churus.",
            "imagen": "img/cena-gatos.jpg"
        },
        {
            "nombre": "Escapada a San Martín de los Andes",
            "precio": 150000,
            "descripcion": "Para visitar a nuestros queridos hermanos, ché.",
            "imagen": "img/san-martin.jpg"
        },
        {
            "nombre": "Ida a Parque Termal Botánico para dos personas",
            "precio": 80000,
            "descripcion": "Ideal para después del matrimonio.",
            "imagen": "img/parque-botanico.jpg"
        },
        {
            "nombre": "Ascenso al Volcán Villarrica (Rukapillán)",
            "precio": 100000,
            "descripcion": "Esto marcaría un hito en nuestra vida en Pucón.",
            "imagen": "img/volcan-villarrica.jpg"
        },
        {
            "nombre": "Camioneta de Leña para el invierno",
            "precio": 100000,
            "descripcion": "Esta helao.",
            "imagen": "img/leña.jpg"
        },
        {
            "nombre": "Estadía en el White Lotus de Sicilia",
            "precio": 200000,
            "descripcion": "Una estadía a lo grande con lo mejor de Cristóbal Tapia de Veer de fondo y un misterioso asesinato en nuestra primera noche (esperamos no ser las víctimas).",
            "imagen": "img/the-white-lotus.jpg"
        },
        {
            "nombre": "Mantención Bicicletas",
            "precio": 100000,
            "descripcion": "Una mantención para nuestras dos bicicletas es una excelente forma de regalonearnos.",
            "imagen": "img/mantencion-bicicletas.jpg"
        },
        {
            "nombre": "Noche de camping en El Cerdúo",
            "precio": 100000,
            "descripcion": "Nuestro lugar de compromiso. Una excelente forma de celebrar el aniversario.",
            "imagen": "img/el-cerduo.jpg"
        },
        {
            "nombre": "Revivir primera cita - Cicletada a San José de Maipo",
            "precio": 40000,
            "descripcion": "Con los deliciosos sandwich de pimentón de la Cote.",
            "imagen": "img/primera-cita.jpg"
        },
        {
            "nombre": "Aperol de litro en la Costa Amalfitana",
            "precio": 40000,
            "descripcion": "Nunca está demás volver a repetirse este plato.",
            "imagen": "img/aperol.jpg"
        },
        {
            "nombre": "Un viaje en tren al sur",
            "precio": 50000,
            "descripcion": "Aprovechando esta nueva forma de viajar, nos encantaría llegar a nuestra casa en un tren.",
            "imagen": "img/tren-al-sur.jpg"
        },
        {
            "nombre": "Una nueva cadera para el Mati",
            "precio": 100000,
            "descripcion": "Para perrear hasta abajo en su matrimonio y poder decirle que sí al Manu en las pichangas.",
            "imagen": "img/cadera.jpg"
        },
        {
            "nombre": "Espada de Acero Valyrio de Jon Snow",
            "precio": 80000,
            "descripcion": "Por si aparecen caminantes blancos en el invierno.",
            "imagen": "img/espada-jon-snow.jpg"
        },
        {
            "nombre": "Sesion de tatuaje para los novios",
            "precio": 50000,
            "descripcion": "Prometemos que los tatuajes no serán en la cara.",
            "imagen": "img/tatoo.jpg"
        },
        {
            "nombre": "Caracola mágica",
            "precio": 30000,
            "descripcion": "Para los momentos de mayor indecisión.",
            "imagen": "img/caracola-magica.jpg"
        },
        {
            "nombre": "Dragón",
            "precio": 100000,
            "descripcion": "Para irse volando a Santiago.",
            "imagen": "img/dragon.jpg"
        },
        {
            "nombre": "Aporte para mejorar receta de Chocapic",
            "precio": 50000,
            "descripcion": "Necesario.",
            "imagen": "img/chocapic.jpg"
        },
        {
            "nombre": "Entrada a parque de Hello Kitty en Japón",
            "precio": 50000,
            "descripcion": "Para nuestra luna de miel.",
            "imagen": "img/hello-kitty.jpg"
        },
        {
            "nombre": "Entrada al Castillo de Osaka en Japón",
            "precio": 50000,
            "descripcion": "Sitio histórico que no podemos perdernos en nuestra luna de miel.",
            "imagen": "img/osaka-castle.jpg"
        },
        {
            "nombre": "Cena de sushi en Tokio",
            "precio": 100000,
            "descripcion": "Para subir la vara del Uber Eats.",
            "imagen": "img/sushi-tokio.jpg"
        },
        {
            "nombre": "Crucero a la Antártica",
            "precio": 200000,
            "descripcion": "El sueño del Mati.",
            "imagen": "img/antartica-cruise.JPG"
        },
        {
            "nombre": "300 hilos de bordado D.M.C.",
            "precio": 70000,
            "descripcion": "Para que la Cote no deje de bordar regalos para sus amigos.",
            "imagen": "img/bordado.jpg"
        },
        {
            "nombre": "Trekking al basecamp del Everest",
            "precio": 150000,
            "descripcion": "Algún día lo lograremos.",
            "imagen": "img/everest.jpg"
        },
        {
            "nombre": "Membresía anual de Churu",
            "precio": 70000,
            "descripcion": "Quién dijo que tener gatos era barato...",
            "imagen": "img/churu.jpg"
        },
        {
            "nombre": "Curso de Cerámica Gres",
            "precio": 60000,
            "descripcion": "Necesitamos hobbies en el sur.",
            "imagen": "img/ceramica.jpg"
        },
        {
            "nombre": "Curso de Patrón de Bahía Deportivo",
            "precio": 50000,
            "descripcion": "Prometemos usar chaleco salvavidas.",
            "imagen": "img/curso-patron.jpg"
        },
        {
            "nombre": "Curso de Elaboración de Cerveza",
            "precio": 50000,
            "descripcion": "Mejor excusa para invitarlos a tomar un shop en la casa bosque.",
            "imagen": "img/cerveza.jpg"
        },
        {
            "nombre": "Entrada a Stand-up de Paloma Salas",
            "precio": 30000,
            "descripcion": "Icónico Camilo Mariguagua.",
            "imagen": "img/paloma-salas.jpg"
        },
        {
            "nombre": "Membresía anual a Estudios Neverland",
            "precio": 50000,
            "descripcion": "No se diga máaas, the table is fucking rolling.",
            "imagen": "img/estudios-neverland.jpg"
        },
        {
            "nombre": "Cafecito con Pedro Pascal",
            "precio": 40000,
            "descripcion": "El sueño de tod@s.",
            "imagen": "img/pedro-pascal.jpg"
        },
        {
            "nombre": "Tren desde Barcelona a Roma",
            "precio": 80000,
            "descripcion": "Para nuestro próximo viaje.",
            "imagen": "img/barcelona-roma.jpeg"
        },
        {
            "nombre": "Un día visitando ropa usada",
            "precio": 30000,
            "descripcion": "Para tener más conciencia amigx.",
            "imagen": "img/ropa-usada.jpg"
        },
        {
            "nombre": "Cena en La Quinta Puerta",
            "precio": 80000,
            "descripcion": "De nuestros lugares favoritos en Pucón.",
            "imagen": "img/quinta-puerta.jpg"
        },
        {
            "nombre": "Luz de check engine que no se prenda más",
            "precio": 50000,
            "descripcion": "Suficiente con este problema. Una luz que no se prenda más nos dejaría tranquilos.",
            "imagen": "img/check-engine.jpg"
        },
        {
            "nombre": "Clases de ski",
            "precio": 50000,
            "descripcion": "Para que la Cote pueda ir a esquiar tranquila al volcán.",
            "imagen": "img/ski.jpg"
        },
        {
            "nombre": "Encendido rápido de la bosca",
            "precio": 30000,
            "descripcion": "Los gatos lo piden.",
            "imagen": "img/bosca.jpg"
        },
        {
            "nombre": "Día de spa y manicure para la Olivia",
            "precio": 30000,
            "descripcion": "La reina de la casa lo necesita de manera mensual.",
            "imagen": "img/olivia.jpg"
        },
        {
            "nombre": "Clases de pesca con Aldo Bravo (con resultados asegurados)",
            "precio": 150000,
            "descripcion": "Basta de promesas incumplidas.",
            "imagen": "img/aldo-bravo.jpg"
        },
        {
            "nombre": "Curso de cocina sin gluten dictado por Jacqueline Yáñez",
            "precio": 100000,
            "descripcion": "Aprenderemos a comer sin hincharnos.",
            "imagen": "img/sin-gluten.jpg"
        },
        {
            "nombre": "Clases de boxeo dictadas por Reinaldo Yáñez",
            "precio": 80000,
            "descripcion": "El abuelo del novio tuvo su época de Rocky Balboa.",
            "imagen": "img/boxeo.jpg"
        },
        {
            "nombre": "Experiencia de bordado con Eliana Valdés",
            "precio": 80000,
            "descripcion": "La abuela del novio posee mucho talento en el área.",
            "imagen": "img/clases-bordado.jpg"
        },
        {
            "nombre": "Viaje para que Martín Bravo traiga el anillo de compromiso",
            "precio": 100000,
            "descripcion": "El testigo del matrimonio y hermano del novio viajó por mar y tierra para hacer esto posible.",
            "imagen": "img/martin-londres.jpg"
        },
        {
            "nombre": "Clase de automaquillaje con Carolina Flores",
            "precio": 100000,
            "descripcion": "La testigo tiene habilidades mágicas para los eventos más importantes.",
            "imagen": "img/caro-makeup.jpg"
        },
        {
            "nombre": "Coctelería de autor con Carolina Flores",
            "precio": 100000,
            "descripcion": "También tiene habilidades mágicas cuando se trata de festejar.",
            "imagen": "img/cocteleria.jpg"
        },
        {
            "nombre": "Curso de Jardinería con Jabu y Dani Villaseñor",
            "precio": 60000,
            "descripcion": "Expertas en los beneficios naturales.",
            "imagen": "img/jardineria.jpg"
        },
        {
            "nombre": "Experiencia turística lacustre por Alejandra Flores",
            "precio": 100000,
            "descripcion": "La mamá de la novia se sabe todas las papitas.",
            "imagen": "img/ale-flores.jpg"
        },
        {
            "nombre": "Sesión de enoturismo para dos",
            "precio": 100000,
            "descripcion": "Aprovechando que estamos en el mejor país de Chile.",
            "imagen": "img/enoturismo.jpg"
        },
        {
            "nombre": "Limpieza dental con Rodrigo Sepúlveda",
            "precio": 50000,
            "descripcion": "Aprovechen de pedirle tarjetas en el matrimonio.",
            "imagen": "img/dental.jpg"
        },
        {
            "nombre": "Clases de golf con Manuel Peralta",
            "precio": 80000,
            "descripcion": "El maestro del swing.",
            "imagen": "img/manu.jpg"
        },
        {
            "nombre": "Dos sesiones de bordado con chicas de los martes",
            "precio": 30000,
            "descripcion": "Gossip y bordado asegurado.",
            "imagen": "img/sesion-bordado.jpg"
        },
        {
            "nombre": "Salir y comer con Rodri y Lucy en Praga",
            "precio": 80000,
            "descripcion": "Nuestros checos favoritos.",
            "imagen": "img/rodri-lucy.jpg"
        },
        {
            "nombre": "Salida de pesca con Tomás Munchmeyer al río Cortaderal",
            "precio": 80000,
            "descripcion": "Truchas, trekking y vinitos en la coordillera.",
            "imagen": "img/tom.jpg"
        },
        {
            "nombre": "30 litros de pisco sour de Carol Dunfort",
            "precio": 60000,
            "descripcion": "Sabemos que es el mejor del mundo.",
            "imagen": "img/carol.jpg"
        },
        {
            "nombre": "Carrot cake de la Tey",
            "precio": 60000,
            "descripcion": "El favorito del novio.",
            "imagen": "img/carrot-cake.jpg"
        },
        {
            "nombre": "Concicerto privado con Cata Martinez y Nacho Manhs",
            "precio": 70000,
            "descripcion": "Un honor escuchar a la pareja de amigos más talentosos que tenemos.",
            "imagen": "img/cata-nacho.jpg"
        },
        {
            "nombre": "Asado en Marbella con Bri y Pia",
            "precio": 70000,
            "descripcion": "La mejor malaya de la zona.",
            "imagen": "img/bri-pia.jpg"
        },
        {
            "nombre": "Arena mágica para gatos",
            "precio": 50000,
            "descripcion": "Elimina olores y suciedad de manera automática.",
            "imagen": "img/arena-gatos.jpg"
        },
        {
            "nombre": "Experiencia en festival de cine con Monse Pais y Coté Munchmeyer",
            "precio": 40000,
            "descripcion": "Para hablar de David Lynch con propiedad.",
            "imagen": "img/sanfic.jpg"
        },
        {
            "nombre": "Noche de karaoke con las chicas Havas",
            "precio": 50000,
            "descripcion": "Calilas, Mojojojos y todas invitadas.",
            "imagen": "img/havas.jpg"
        },
        {
            "nombre": "Clases de DJ con Diego Paredes",
            "precio": 50000,
            "descripcion": "Mejor DJ de Santiago.",
            "imagen": "img/diego.jpg"
        },
        {
            "nombre": "Ida a bailar con Diego y Mari",
            "precio": 50000,
            "descripcion": "Esta pareja explosiva se saca los prohibidos.",
            "imagen": "img/diego-mari.jpg"
        },
        {
            "nombre": "Experiencia de kayak con Maximiliano Hebel",
            "precio": 70000,
            "descripcion": "El mejor guía de la región de Los Lagos.",
            "imagen": "img/max.jpg"
        },
        {
            "nombre": "Clases de ajedrez con Benjamín Rizzardini",
            "precio": 70000,
            "descripcion": "Dicen que ni Anya Taylor-Joy puede contra este maestro.",
            "imagen": "img/benja.jpg"
        },
        {
            "nombre": "Atención veterinaria a domicilio con Yoyo",
            "precio": 50000,
            "descripcion": "El hermano de la novia es el mejor para dejar a nuestras mascotas.",
            "imagen": "img/yoyo.jpg"
        },
        {
            "nombre": "Clases de canto con Carla Bravo",
            "precio": 50000,
            "descripcion": "La hermana del novio tiene talentos musicales.",
            "imagen": "img/carla.jpg"
        },
        {
            "nombre": "Asadito en Reñaca con Toto y Diane",
            "precio": 100000,
            "descripcion": "Los mejores asados de la región costera central.",
            "imagen": "img/toto.jpg"
        },
        {
            "nombre": "Día de shopping con Vivi Flores",
            "precio": 100000,
            "descripcion": "Panorama muy entretenido para cualquier día.",
            "imagen": "img/vivi.jpg"
        },
        {
            "nombre": "Degustación de cerveza CCU junto a Mati y Gabi",
            "precio": 100000,
            "descripcion": "Expertos en fermentación de cebada.",
            "imagen": "img/mati-gabi.jpg"
        },
        {
            "nombre": "Carrete con Tente Villaseñor",
            "precio": 50000,
            "descripcion": "Nos asegurarán la mejor noche de carrete de nuestras vidas.",
            "imagen": "img/tente.jpg"
        },
        {
            "nombre": "Membresía anual Alto del Carmen con Bruno Lapi",
            "precio": 70000,
            "descripcion": "El hombre sabe lo que es bueno en calidad y cantidad.",
            "imagen": "img/bruno.jpg"
        },
        {
            "nombre": "Clase de biodanza con Víctor Gomez",
            "precio": 70000,
            "descripcion": "Directo desde Ñuñoa.",
            "imagen": "img/biodanza.jpg"
        },
        {
            "nombre": "Clase de batería con Juan Cristobal Garretón",
            "precio": 70000,
            "descripcion": "El maestro del hi hat directo desde Valdivia.",
            "imagen": "img/bateria.jpg"
        },
        {
            "nombre": "Expedición en bicicleta con Gisela Quiroz",
            "precio": 70000,
            "descripcion": "Tiene todas las papitas de las buenas rutas.",
            "imagen": "img/bici-exp.jpg"
        },
        {
            "nombre": "Expedición de trail runing con Javiera Valderrama",
            "precio": 70000,
            "descripcion": "Vamos a intentar mantenerle el ritmo.",
            "imagen": "img/trail.jpg"
        },
        {
            "nombre": "Entrenamiento personalizado con Graci y Andrés",
            "precio": 80000,
            "descripcion": "Expertos en el deporte y la educación.",
            "imagen": "img/graci-andres.jpg"
        },
        {
            "nombre": "Cubicación de materiales para invernadero con Javiera Perry",
            "precio": 50000,
            "descripcion": "Esas planillas no se harán solas...",
            "imagen": "img/perry.jpg"
        },
        {
            "nombre": "Asesoría legal con Javiera Ilabaca",
            "precio": 50000,
            "descripcion": "Primera opción cuando se trata de defendernos.",
            "imagen": "img/jaji.jpg"
        },
        {
            "nombre": "Clases de carpintería dictadas por Sven Kroneberg",
            "precio": 100000,
            "descripcion": "Para fabricar nuestros propios muebles y botes.",
            "imagen": "img/sven.jpg"
        },
        {
            "nombre": "Curso de Apicultura con Vero González",
            "precio": 100000,
            "descripcion": "Para aprender a hacer la mejor miel del sur.",
            "imagen": "img/apicultura.jpg"
        },
        {
            "nombre": "Tocata impartida por Caces",
            "precio": 50000,
            "descripcion": "El hombre de los mil y un talentos.",
            "imagen": "img/caces.jpg"
        },
        {
            "nombre": "Travesía fotográfica con Martín Bravo",
            "precio": 50000,
            "descripcion": "El testigo del matrimonio tiene un muy buen ojo fotográfico.",
            "imagen": "img/martin-foto.jpg"
        },
        {
            "nombre": "Lectura de tarot con Paula",
            "precio": 30000,
            "descripcion": "La Paula adivinó este matrimonio, así que hay resultados garantizados.",
            "imagen": "img/paula.jpg"
        },
        {
            "nombre": "Clases de primeros auxilios con Jacqueline Yáñez",
            "precio": 50000,
            "descripcion": "Tenemos una médico experta en la familia.",
            "imagen": "img/jacki.jpg"
        },
        {
            "nombre": "Lectura de carta astral por Rodrigo Sepúlveda",
            "precio": 35000,
            "descripcion": "El papá de la novia es mejor que Pedrito Engel.",
            "imagen": "img/rodrigo-astral.jpg"
        },
        {
            "nombre": "Visita guiada a viña con Alejandra Flores",
            "precio": 80000,
            "descripcion": "Los mejores consejos para encontrar un gran vino de 6 mil pesos en el supermercado.",
            "imagen": "img/ale-viña.jpg"
        },
        {
            "nombre": "Sesión de Catán con Camila Caro",
            "precio": 50000,
            "descripcion": "Nos asegura que se dejará perder.",
            "imagen": "img/catan.jpg"
        },
        {
            "nombre": "Noche de piscolas con las k-bras",
            "precio": 50000,
            "descripcion": "Cuesta mantenerles el ritmo, pero lo intentaremos.",
            "imagen": "img/kbras.jpg"
        },
        {
            "nombre": "Sesión de ácido hialurónico con la Doctora Barrios",
            "precio": 70000,
            "descripcion": "Experta en que la vejéz pase piola.",
            "imagen": "img/igna.jpg"
        },
        {
            "nombre": "Sesión Tratamiento Invisaling con el doctor Flores",
            "precio": 70000,
            "descripcion": "Nuestro dentista influencer de la familia.",
            "imagen": "img/andres.jpg"
        },
        {
            "nombre": "Tarde de quesadillas con Pipe, Isi y Emi",
            "precio": 70000,
            "descripcion": "Para compartir una linda tarde escuchando las risas de la Emi.",
            "imagen": "img/pipe-isi.jpg"
        },
        {
            "nombre": "Asesoría Nutricional con María Ignacia Flores",
            "precio": 70000,
            "descripcion": "Hay que bajar los kilos post matrimonio.",
            "imagen": "img/nacha.jpg"
        },
        {
            "nombre": "Libro de recetas Nutritoti",
            "precio": 70000,
            "descripcion": "Se aseguran galletas con chips de chocolates sin grasas, harinas ni azúcares.",
            "imagen": "img/toti.jpg"
        },
        {
            "nombre": "Tarde con Cami Villaseñor, Luciano y Lari en el bosque",
            "precio": 50000,
            "descripcion": "Esperamos las indicaciones de Lu para llevarnos por los mejores senderos.",
            "imagen": "img/cami-villa.jpg"
        },
        {
            "nombre": "Coaching laboral con Cata y Coti",
            "precio": 100000,
            "descripcion": "Nuestras expertas en clima y cultura organizacional.",
            "imagen": "img/cata-coti.jpg"
        },
        {
            "nombre": "Experiencia de prueba",
            "precio": 1000,
            "descripcion": "test.",
            "imagen": "img/test.jpg"
        },
        
    ]
    
    for exp in experiencias:
        exp["regalado"] = exp["nombre"] in experiencias_confirmadas

    return render_template("index.html", experiencias=experiencias)

def confirmar_desde_correo(texto_email):
    cargar_regalos()
    print(f"🔍 Hay {len(regalos)} regalos en memoria", flush=True)
    # Buscar patrón del tipo $1.000 o $120000
    match = re.search(r"\$[\d\.]+", texto_email)
    if not match:
        print("❌ No se encontró monto en el correo", flush=True)
        return

    monto_str = match.group(0).replace("$", "").replace(".", "")
    try:
        monto = int(monto_str)
    except ValueError:
        print("❌ No se pudo convertir el monto:", monto_str, flush=True)
        return

    ahora = datetime.now()
    umbral_tiempo = ahora - timedelta(minutes=5)  # revisar regalos creados hace menos de 5 minutos

    print(f"📬 Monto detectado en correo: {monto}", flush=True)
    print("🎁 Regalos pendientes recientes:", flush=True)

    for r in regalos:
        # if not r.get("confirmado") and r["fecha"] >= umbral_tiempo:
        if not r.get("confirmado"):    
            total = sum(exp["precio"] for exp in r["experiencias"])
            print(f"- {r['nombre']}: ${total}", flush=True)
            if abs(total - monto) <= 1000:  # tolerancia
                r["confirmado"] = True
                for e in r["experiencias"]:
                    experiencias_regaladas.add(e["nombre"])
                print(f"✅ Confirmado regalo por monto: ${monto:,} de {r['nombre']}", flush=True)
                enviar_correos_de_agradecimiento(r["nombre"], r["correo"], r["mensaje"], r["experiencias"], total)
                # Actualizar el archivo regalos.json con el cambio de estado
                with open("regalos.json", "w", encoding="utf-8") as f:
                    regalos_guardar = [
                        {**reg, "fecha": reg["fecha"].isoformat()} for reg in regalos
                    ]
                    json.dump(regalos_guardar, f, indent=2, ensure_ascii=False)
                break
        else:
            print("⚠️ No se encontró ningún regalo reciente pendiente con ese monto.", flush=True)

@app.route('/agregar', methods=['POST'])
def agregar_al_carrito():
    nombre = request.form.get('nombre_exp')
    precio = int(request.form.get('precio_exp'))
    descripcion = request.form.get('descripcion_exp')

    item = {"nombre": nombre, "precio": precio, "descripcion": descripcion}

    if 'carrito' not in session:
        session['carrito'] = []
    session['carrito'].append(item)
    session.modified = True

    return redirect(url_for('carrito'))

@app.route('/carrito')
def carrito():
    items = session.get('carrito', [])
    total = sum(item['precio'] for item in items)
    return render_template("carrito.html", items=items, total=total)

@app.route('/eliminar/<int:indice>', methods=['POST'])
def eliminar_experiencia(indice):
    if 'carrito' in session:
        try:
            session['carrito'].pop(indice)
            session.modified = True
        except IndexError:
            pass  # índice fuera de rango
    return redirect(url_for('carrito'))

import requests
import json

@app.route('/pagar', methods=["POST"])
def pagar():
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for('carrito'))

    total = sum(item['precio'] for item in carrito)
    nombre = request.form.get("nombre")
    mensaje = request.form.get("mensaje")
    correo_usuario = request.form.get("correo")

    regalo = {
        "nombre": nombre,
        "correo": correo_usuario,
        "experiencias": [item.copy() for item in carrito],
        "mensaje": mensaje,
        "fecha": datetime.now(),
        "confirmado": False
    }

    regalos.append(regalo)
    with open("regalos.json", "w", encoding="utf-8") as f:
        # Convertir datetime a string antes de guardar
        regalos_guardar = [
            {**r, "fecha": r["fecha"].isoformat()} for r in regalos
        ]
        json.dump(regalos_guardar, f, indent=2, ensure_ascii=False)
    regalo_id = len(regalos) - 1
    session['regalo_actual_id'] = regalo_id
    session['total_a_pagar'] = total

    # Redirige a Slach directamente
    return redirect(f"https://slach.cl/mati-cote-regalos/{total}")

@app.route('/verificar_pago')
def verificar_pago():
    idx = session.get('regalo_actual_id')
    if idx is not None and 0 <= idx < len(regalos):
        return {"confirmado": regalos[idx]["confirmado"]}
    return {"confirmado": False}

def enviar_correos_de_agradecimiento(nombre, correo_usuario, mensaje, experiencias, total):
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USER = "maticoteregalos@gmail.com"
    EMAIL_PASS = "qlhx kwrt kwxx pgap"

    EMAILS_DESTINO_NOVIOS = ["mjbravo4@uc.cl", "josefinasepulvedaf@gmail.com"]  # <- agrega el correo de tu novia real

    # ---------- Correo para los novios ----------
    subject_novios = f"🎁 Nuevo regalo de {nombre}"
    body_novios = f"""Hola, recibiste un nuevo regalo:

👤 Nombre: {nombre}
📧 Correo: {correo_usuario}
💬 Mensaje: {mensaje}

🎉 Experiencias regaladas:"""

    for exp in experiencias:
        body_novios += f"\n- {exp['nombre']} (${exp['precio']:,})"

    body_novios += f"\n\n💰 Total: ${total:,} CLP\n\n¡Revisa Slach para confirmar el pago! 💚"

    msg_novios = MIMEMultipart()
    msg_novios["From"] = EMAIL_USER
    msg_novios["To"] = ", ".join(EMAILS_DESTINO_NOVIOS)
    msg_novios["Subject"] = subject_novios
    msg_novios.attach(MIMEText(body_novios, "plain"))

    # ---------- Correo de agradecimiento para quien regaló ----------
    subject_user = "🎁 ¡Gracias por tu regalo!"
    body_user = f"""Hola {nombre},

Queremos agradecerte profundamente por tu regalo 💚

🎉 Experiencias que nos regalaste:
"""
    for exp in experiencias:
        body_user += f"- {exp['nombre']} (${exp['precio']:,})\n"

    body_user += f"""
💬 Tu mensaje:
"{mensaje}"

Gracias por formar parte de este momento tan especial.
Con cariño,
Mati & Cote 💕
"""

    msg_user = MIMEMultipart()
    msg_user["From"] = EMAIL_USER
    msg_user["To"] = correo_usuario
    msg_user["Subject"] = subject_user
    msg_user.attach(MIMEText(body_user, "plain"))

    # Agregar imagen (opcional)
    from email.mime.image import MIMEImage
    try:
        with open("static/img/nosotros_gracias.jpg", "rb") as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<graciasimg>')
            msg_user.attach(img)
    except Exception as e:
        print("No se pudo adjuntar imagen:", e, flush=True)

    # ---------- Enviar ambos correos ----------
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        for correo in EMAILS_DESTINO_NOVIOS:
            server.sendmail(EMAIL_USER, correo, msg_novios.as_string())
        server.sendmail(EMAIL_USER, correo_usuario, msg_user.as_string())
        server.quit()
        print("📬 Correos enviados con éxito.", flush=True)
    except Exception as e:
        print("❌ Error al enviar correos:", e, flush=True)


if __name__ == '__main__':
    app.run(debug=True)
