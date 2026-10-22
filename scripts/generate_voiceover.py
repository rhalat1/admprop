import asyncio
import edge_tts
import subprocess
import imageio_ffmpeg

VOICEOVER_PARTS = [
    ("scene1", "¿Te imaginas construir la casa de tus sueños en el Urubó? Te presento esta increíble oportunidad en la Urbanización Privada Bella Flor."),
    ("scene2", "Una ubicación privilegiada, a tan solo ocho minutos del cuarto anillo, con cuatro kilómetros de ruta totalmente asfaltada."),
    ("scene3", "Un condominio exclusivo y seguro, con control de acceso las veinticuatro horas y vías pavimentadas."),
    ("scene4", "Cuenta con un terreno de setecientos cuatro metros cuadrados, cien por ciento plano y casi veinte metros de frente."),
    ("scene5", "El espacio perfecto para edificar una moderna residencia minimalista, con jardín y piscina privada."),
    ("scene6", "Además, disfrutarás de piscinas tipo resort, club house con churrasqueras, y canchas de tenis y fútbol iluminadas."),
    ("scene7", "Documentación al día con Folio Real individual listo para transferir, a un precio de ocasión de noventa y cuatro mil cuatrocientos dólares."),
    ("scene8", "Soy Roxana Pozo de Century 21 Invictus. Comenta la palabra INFO en este video o contáctame al enlace del perfil para agendar tu visita.")
]

async def generate_voiceovers():
    total_duration = 0
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    
    file_list = []
    for tag, text in VOICEOVER_PARTS:
        filename = f"public/urubo-bella-flor/images/vo_{tag}.mp3"
        comm = edge_tts.Communicate(text, "es-BO-SofiaNeural", rate="+3%", pitch="+0Hz")
        await comm.save(filename)
        
        # probe duration
        res = subprocess.run([ffmpeg, "-i", filename], capture_output=True, text=True)
        # find Duration: 00:00:04.56
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        dur = 0
        if m:
            dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
        print(f"{tag}: {dur:.2f}s -> {text[:40]}...")
        file_list.append((filename, dur))
        total_duration += dur

    print(f"\nTotal raw voiceover duration: {total_duration:.2f}s")

if __name__ == "__main__":
    asyncio.run(generate_voiceovers())
