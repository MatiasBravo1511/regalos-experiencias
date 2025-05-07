from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import chardet
import time
    

# Configuración de Gmail IMAP
EMAIL_USER = "maticoteregalos@gmail.com"
EMAIL_PASS = "qlhx kwrt kwxx pgap"
IMAP_SERVER = "imap.gmail.com"

def leer_emails_y_confirmar(callback_confirmar):
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

                    print("📨 Asunto:", subject)
                    print("🧾 Cuerpo:", cuerpo[:300])  # muestra los primeros 300 caracteres

                    # FILTRO: si contiene "Slach" o un nombre conocido
                    if "slach" in subject.lower() or "slach" in cuerpo.lower():
                        print(f"📥 Detectado correo relacionado a pago: {subject}")
                        callback_confirmar(subject + cuerpo)

        mail.logout()
    except Exception as e:
        print("❌ Error al leer correos:", e)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para mantener la sesión segura

# Simularemos una "base de datos" en memoria para guardar los mensajes
regalos = []
experiencias_regaladas = set()

@app.route('/')
def index():
    experiencias = [
        {
            "nombre": "Cena Romántica en Hotel Antumalal",
            "precio": 80000,
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
            "precio": 150000,
            "descripcion": "Para poder revivir uno de nuestros primeros (y más sufridos) viajes por Chile.",
            "imagen": "img/cicloturismo.jpg"
        },
        {
            "nombre": "Curso de Carpintería para el Mati",
            "precio": 50000,
            "descripcion": "",
            "imagen": "img/carpinteria.jpg"
        },
        {
            "nombre": "Curso de Jardinería para la Cote",
            "precio": 50000,
            "descripcion": "",
            "imagen": "img/jardineria.jpg"
        },
        {
            "nombre": "Curso de Apicultura",
            "precio": 100000,
            "descripcion": "",
            "imagen": "img/apicultura.jpg"
        },
        {
            "nombre": "Curso de Compostaje",
            "precio": 100000,
            "descripcion": "",
            "imagen": "img/compostaje.jpg"
        },
        {
            "nombre": "Invernadero para el bosque",
            "precio": 80000,
            "descripcion": "",
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
            "descripcion": "",
            "imagen": "img/erlend-oye.jpg"
        },
        {
            "nombre": "Concierto privado de Cristóbal Briceño",
            "precio": 80000,
            "descripcion": "",
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
            "descripcion": "",
            "imagen": "img/aeropress.jpg"
        },
        {
            "nombre": "Saco de café de grano",
            "precio": 50000,
            "descripcion": "",
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
            "descripcion": "Para visitar a nuestros queridos hermanos, boludo.",
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
            "descripcion": "Porque esta helao.",
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
            "nombre": "Noche de camping en El Cerduo",
            "precio": 100000,
            "descripcion": "Nuestro lugar de compromiso. Una excelente forma de celebrar el aniversario.",
            "imagen": "img/el-cerduo.jpg"
        },
        {
            "nombre": "Revivir primera cita - Cicletada a San José de Maipo",
            "precio": 30000,
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
            "descripcion": "",
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
            "precio": 40000,
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
            "descripcion": "",
            "imagen": "img/sushi-tokio.jpg"
        },
        {
            "nombre": "Crucero a la Antártica",
            "precio": 200000,
            "descripcion": "El sueño del Mati.",
            "imagen": "img/antartica-cruise.jpg"
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
            "descripcion": "Necesitamos hobbies en el sur",
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
            "descripcion": "Mejor excusa para invitarlos a tomar un Shop en la casa bosque.",
            "imagen": "img/cerveza.jpg"
        },
        {
            "nombre": "Entrada a Stand-up de Paloma Salas",
            "precio": 30000,
            "descripcion": "Siempre es bueno reirse.",
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
            "precio": 30000,
            "descripcion": "El sueño de tod@s.",
            "imagen": "img/pedro-pascal.jpg"
        },
        {
            "nombre": "Tren desde Barcelona a Roma",
            "precio": 50000,
            "descripcion": "Para nuestro próximo viaje.",
            "imagen": "img/barcelona-roma.jpeg"
        },
        {
            "nombre": "Un día visitando ropa usada",
            "precio": 20000,
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
            "precio": 20000,
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
            "precio": 100000,
            "descripcion": "Basta de promesas incumplidas.",
            "imagen": "img/aldo-bravo.jpg"
        },
        {
            "nombre": "Curso de cocina sin gluten dictado por Jacqueline Yáñez",
            "precio": 100000,
            "descripcion": "Puro talento por acá.",
            "imagen": "img/test.jpg"
        },
        {
            "nombre": "Clases de boxeo dictadas por Reinaldo Yáñez",
            "precio": 100000,
            "descripcion": "El abuelo del novio tuvo su época de Rocky Balboa.",
            "imagen": "img/boxeo.jpg"
        },
        {
            "nombre": "Experiencia de bordado con Eliana Valdés",
            "precio": 50000,
            "descripcion": "La abuela del novio posee mucho talento en el área.",
            "imagen": "img/clases-bordado.jpg"
        },
        {
            "nombre": "Viaje para que Martín Bravo traiga el anillo de compromiso",
            "precio": 100000,
            "descripcion": "El testigo del matrimonio viajó por mar y tierra para hacer esto posible.",
            "imagen": "img/test.jpg"
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
            "nombre": "Experiencia turística lacustre por Alejandra Flores",
            "precio": 100000,
            "descripcion": "La mamá de la novia es la mejor guía turística.",
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
            "precio": 100000,
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
            "precio": 40000,
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
            "precio": 80000,
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
            "precio": 100000,
            "descripcion": "Esta pareja explosiva se saca los prohibidos.",
            "imagen": "img/diego-mari.jpg"
        },
        {
            "nombre": "Experiencia de kayak con Maximiliano Hebel",
            "precio": 100000,
            "descripcion": "El mejor guía de la región de Los Lagos.",
            "imagen": "img/max.jpg"
        },
        {
            "nombre": "Clases de ajedrez con Benjamín Rizzardini",
            "precio": 100000,
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
            "nombre": "Asadito en Reñaca con Toto y Dayan",
            "precio": 80000,
            "descripcion": "Los mejores asados de la región costera central.",
            "imagen": "img/toto.jpg"
        },
        {
            "nombre": "Día de shopping con Vivi Flores",
            "precio": 70000,
            "descripcion": "Panorama muy entretenido para cualquier día.",
            "imagen": "img/vivi.jpg"
        },
        {
            "nombre": "Degustación de cerveza CCU junto a Mati y Gabi",
            "precio": 80000,
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
            "precio": 100000,
            "descripcion": "El hombre sabe lo que es bueno en calidad y cantidad.",
            "imagen": "img/bruno.jpg"
        },
        {
            "nombre": "Clase de biodanza con Víctor Gomez",
            "precio": 50000,
            "descripcion": "Directo desde Ñuñoa.",
            "imagen": "img/biodanza.jpg"
        },
        {
            "nombre": "Entrenamiento personalizado con Graci y Andrés",
            "precio": 100000,
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
            "precio": 100000,
            "descripcion": "Primera opción cuando se trata de defendernos.",
            "imagen": "img/jaji.jpg"
        },
        {
            "nombre": "Clases de carpintería dictadas por Sven Kroneberg",
            "precio": 50000,
            "descripcion": "Para fabricar nuestros propios muebles y botes.",
            "imagen": "img/sven.jpg"
        },
        {
            "nombre": "Tocata impartida por Caces",
            "precio": 50000,
            "descripcion": "Porque el hombre pinta, escribe poesía, guitarrea, canta y toca guitarra.",
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
            "precio": 30000,
            "descripcion": "Mejor que Pedrito Engel.",
            "imagen": "img/rodrigo-astral.jpg"
        },
        {
            "nombre": "Visita guiada a viña con Alejandra Flores",
            "precio": 80000,
            "descripcion": "Los mejores consejos para encontrar un gran vino de 6 mil pesos.",
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
            "nombre": "Experiencia de prueba",
            "precio": 1000,
            "descripcion": "test.",
            "imagen": "img/test.jpg"
        },
        
    ]
    for exp in experiencias:
        exp["regalado"] = exp["nombre"] in experiencias_regaladas
    return render_template("index.html", experiencias=experiencias)

import re

def confirmar_desde_correo(texto_email):
    # Buscar patrón del tipo $1.000 o $120000
    match = re.search(r"\$[\d\.]+", texto_email)
    if not match:
        print("❌ No se encontró monto en el correo")
        return

    monto_str = match.group(0).replace("$", "").replace(".", "")
    try:
        monto = int(monto_str)
    except ValueError:
        print("❌ No se pudo convertir el monto:", monto_str)
        return

    print(f"📬 Monto detectado en correo: {monto}")
    
    print("🎁 Regalos pendientes:")
    for r in regalos:
        if not r.get("confirmado"):
            total = sum(exp["precio"] for exp in r["experiencias"])
            print(f"- {r['nombre']}: ${total}")
            if total == monto:
                r["confirmado"] = True
                for e in r["experiencias"]:
                    experiencias_regaladas.add(e["nombre"])
                print(f"✅ Confirmado regalo por monto: ${monto:,} de {r['nombre']}")

                # Enviar correo recién ahora
                enviar_correos_de_agradecimiento(r["nombre"], r["correo"], r["mensaje"], r["experiencias"], total)
                break
    else:
        print(f"⚠️ No se encontró ningún regalo pendiente con ese monto. Monto detectado: ${monto}")
        print(f"Totales pendientes: {[sum(exp['precio'] for exp in r['experiencias']) for r in regalos if not r.get('confirmado')]}")



@app.route('/enviar_regalo', methods=["POST"])
def enviar_regalo():
    nombre = request.form.get("nombre")
    mensaje = request.form.get("mensaje")
    carrito = session.get('carrito', [])

    regalos.append({
        "nombre": nombre,
        "experiencias": carrito,
        "mensaje": mensaje,
        "fecha": datetime.now(),
        "confirmado": False
    })

    session.pop('carrito', None)  # vacía el carrito después de enviar

    return redirect(url_for("gracias"))


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

@app.route('/gracias')
def gracias():
    return render_template("gracias.html")

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


import hashlib
def generar_firma(params, secret):
    # No incluir el parámetro 's' en la firma
    parametros_para_firma = {k: v for k, v in params.items() if k != 's'}

    # Orden alfabético por clave
    sorted_items = sorted(parametros_para_firma.items())

    # Concatenar como key=value
    concatenado = '&'.join(f"{k}={v}" for k, v in sorted_items)

    # Agregar secret key al final
    concatenado += secret

    # Generar firma SHA-256 en hexadecimal
    return hashlib.sha256(concatenado.encode('utf-8')).hexdigest()

@app.route('/confirmar_pago', methods=['POST'])
def confirmar_pago():
    return "OK"

@app.route('/pago_confirmacion')
def pago_confirmacion():
    total = session.get('total_a_pagar', 0)
    idx = session.get('regalo_actual_id')
    nombre = regalos[idx]["nombre"] if idx is not None and idx < len(regalos) else "Amigo/a"
    return render_template("pago_confirmacion.html", total=total, nombre=nombre)


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
        print("No se pudo adjuntar imagen:", e)

    # ---------- Enviar ambos correos ----------
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        for correo in EMAILS_DESTINO_NOVIOS:
            server.sendmail(EMAIL_USER, correo, msg_novios.as_string())
        server.sendmail(EMAIL_USER, correo_usuario, msg_user.as_string())
        server.quit()
        print("📬 Correos enviados con éxito.")
    except Exception as e:
        print("❌ Error al enviar correos:", e)


if __name__ == '__main__':
    import threading

    def iniciar_lector_correos():
        def bucle_verificacion():
            while True:
                for _ in range(15):  # intenta durante 5 minutos (15*20s)
                    leer_emails_y_confirmar(confirmar_desde_correo)
                    time.sleep(20)

        hilo = threading.Thread(target=bucle_verificacion, daemon=True)
        hilo.start()

    # Iniciar el lector de correos antes de arrancar Flask
    iniciar_lector_correos()
    app.run(debug=True)
