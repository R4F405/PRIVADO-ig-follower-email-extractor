# Extractor de Correos de Seguidores de Instagram

**AVISO IMPORTANTE**: Este proyecto es solo para fines educativos y de investigación. El uso de este software para extraer datos de manera masiva de Instagram va en contra de los Términos de Servicio de Instagram. Este repositorio es privado y no debe compartirse públicamente.

## Descripción

Esta herramienta automatiza el proceso de identificación de correos electrónicos asociados a perfiles de Instagram que siguen a un usuario específico. Utiliza técnicas de web scraping a través de Selenium para:

1. Iniciar sesión en Instagram usando credenciales proporcionadas
2. Navegar al perfil objetivo
3. Extraer la lista de seguidores
4. Visitar cada perfil de seguidor
5. Buscar correos electrónicos en sus biografías
6. Guardar los resultados en formato CSV

## Estructura del Repositorio

- **ExtractorCorreosInstagram.py**: Script principal con toda la lógica de extracción de datos
- **requirements.txt**: Archivo de dependencias (Selenium)
- **seguidores.txt**: Almacena la lista de nombres de usuario de seguidores
- **emails_encontrados.txt**: Guarda los correos encontrados durante la ejecución
- **instagram_emails.csv**: Archivo CSV con resultados (usuario, correo, URL de perfil)

## Funcionalidades

- **Inicio de sesión automático**: Maneja cookies y formularios de login
- **Extracción de seguidores**: Desplazamiento automático para cargar todos los seguidores
- **Detección de correos**: Algoritmos avanzados para identificar correos en diferentes formatos:
  - Correos estándar (ejemplo@dominio.com)
  - Correos con protección anti-bots ([at], (at), arroba, etc.)
  - Correos con prefijos (email:, correo:, etc.)
- **Gestión de límites**: Pausas aleatorias para evitar bloqueos
- **Manejo de errores**: Capturas de pantalla automáticas al detectar problemas

## Requisitos

- Python 3.6+
- Selenium
- Chrome para testing (Chrome WebDriver)

## Instalación

1. Clona este repositorio
2. Crea un entorno virtual:
   ```
   python -m venv venv
   ```
3. Activa el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
5. Descarga e instala Chrome WebDriver:
   - Visita https://chromedriver.chromium.org/downloads o https://googlechromelabs.github.io/chrome-for-testing/
   - Descarga la versión de ChromeDriver que coincida exactamente con tu versión de Chrome
   - Debes descargar con nombre de la columna Binary -> chrome
   - Para verificar tu versión de Chrome, abre Chrome y ve a: ⋮ > Ayuda > Acerca de Google Chrome
   - Descomprime el archivo descargado y guarda el ejecutable en una ubicación conocida
   - Debes añadir la ruta absoluta hasta el chrome.exe
   - Esta ruta del ejecutable es la que deberás proporcionar al ejecutar el script

## Uso

1. Ejecuta el script principal:
   ```
   python ExtractorCorreosInstagram.py
   ```
2. Introduce tu nombre de usuario y contraseña de Instagram
3. Proporciona la URL del perfil cuyos seguidores deseas analizar
4. Indica la ruta completa al ejecutable de Chrome WebDriver

## Archivos de Salida

- **instagram_emails.csv**: Contiene tres columnas: Username, Email, Profile URL
- **seguidores.txt**: Lista simple de nombres de usuario de seguidores
- **emails_encontrados.txt**: Correos encontrados en formato "usuario: correo@ejemplo.com"

## Advertencias Legales

- Este software solo debe usarse con perfiles donde tengas permiso explícito del propietario
- La extracción masiva de datos va contra los términos de servicio de Instagram
- El uso indebido puede resultar en la suspensión de tu cuenta de Instagram
- El autor no se hace responsable del mal uso de esta herramienta

## Limitaciones

- Instagram puede detectar comportamientos automatizados y bloquear la sesión
- La herramienta está limitada a procesar 100 perfiles por ejecución para evitar restricciones
- No todos los usuarios tienen correos visibles en sus perfiles

## Notas Técnicas

El script utiliza técnicas de espera, pausas aleatorias y simulación de comportamiento humano para reducir la probabilidad de detección como bot. Sin embargo, no hay garantía de que Instagram no detecte la actividad automatizada. 
