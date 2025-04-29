import re
import time
import csv
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

def extract_email_from_text(text):
    patterns = [
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Estándar
        r"[a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,}",  # Con espacios
        r"[a-zA-Z0-9._%+-]+\s*(?:\[\s*at\s*\]|\(at\)|\(en\)| at | EN )\s*[a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,}",  # Variaciones [at]
        r"(?:mail|email|correo|e-mail|E-Mail|MAIL):\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Prefijos comunes
        r"[a-zA-Z0-9._%+-]+\s*(?:ar?roba|ARROBA)\s*[a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,}"  # "arroba" en texto
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            email = match.group(0)
            # Normalización
            email = re.sub(r'\s+', '', email)
            email = email.replace("[at]", "@").replace("(at)", "@").replace(" at ", "@")
            email = email.replace("[arroba]", "@").replace("(arroba)", "@").replace("arroba", "@")
            email = re.sub(r'^(mail:|email:|correo:)\s*', '', email, flags=re.IGNORECASE)
            return email
    return None

def extract_instagram_emails(username, password, profile_url, chrome_for_testing_path, output_file="perfiles.csv"):
    driver = None
    try:
        # Configuración avanzada del navegador
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = chrome_for_testing_path
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-save-password-bubble")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        })
        print("🚀 Iniciando navegador Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        print("✅ Navegador iniciado correctamente")

        # Proceso de login
        print("🔑 Iniciando sesión en Instagram...")
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(random.uniform(3, 5))

        # Manejar cookies
        try:
            cookie_xpaths = [
                "//button[contains(text(), 'Allow')]",
                "//button[contains(text(), 'Permitir')]",
                "//button[contains(text(), 'Aceptar')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(@class, '_a9-- _a9_1')]"
            ]
            for xpath in cookie_xpaths:
                try:
                    cookie_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    cookie_button.click()
                    print("🍪 Cookies aceptadas")
                    time.sleep(random.uniform(1, 2))
                    break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ No se encontró popup de cookies: {str(e)[:50]}")

        # Rellenar credenciales de forma humana
        try:
            username_field = WebDriverWait(driver, 4.7).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = driver.find_element(By.NAME, "password")
            print("⌨️ Escribiendo credenciales...")
            for char in username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            time.sleep(random.uniform(0.5, 1.5))
            for char in password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            time.sleep(random.uniform(0.5, 1.5))
            password_field.send_keys(Keys.RETURN)
            print("🔑 Credenciales enviadas")
        except Exception as e:
            print(f"❌ Error en login: {str(e)[:100]}")
            return

        # Verificar login exitoso
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[contains(@aria-label, 'Home') or "
                                                "contains(@href, '/accounts/activity/') or "
                                                "//*[contains(text(), 'Inicio') or contains(text(), 'Home')]]"))
            )
            print("🎉 Login exitoso confirmado")
            time.sleep(random.uniform(3, 6))
        except TimeoutException:
            print("❌ No se pudo confirmar el login")
            driver.save_screenshot("login_error.png")
            print("📸 Captura de pantalla guardada como login_error.png")
            return

        # Navegar al perfil objetivo
        print(f"🔍 Accediendo al perfil: {profile_url}")
        driver.get(profile_url)
        time.sleep(random.uniform(4, 7))

        # Solución mejorada para el botón de seguidores
        print("👥 Buscando botón de seguidores...")
        try:
            followers_button_xpaths = [
                "//a[contains(@href, '/followers/')]",
                "//a[contains(@href, '/followers/')]/span",
                "//li[contains(@class, 'x78zum5')]/a[contains(@href, '/followers/')]",
                "//div[contains(@class, 'x9f619"
                "')]/div/ul/li[2]/a",
                "//div[contains(@class, 'x78zum5')]/a[contains(@href, '/followers/')]",
                "//a[contains(@href, '/followers/')]/div/span"
            ]
            clicked = False
            for xpath in followers_button_xpaths:
                try:
                    followers_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", followers_button)
                    time.sleep(random.uniform(1, 2))
                    driver.execute_script("arguments[0].click();", followers_button)
                    clicked = True
                    print("✅ Botón de seguidores clickeado")
                    break
                except Exception as e:
                    print(f"⚠️ Selector {xpath} falló: {str(e)[:30]}")
                    continue
            if not clicked:
                print("🔄 Intentando método alternativo para clic en seguidores...")
                driver.execute_script('''
                    const links = document.querySelectorAll('a');
                    for (const link of links) {
                        if (link.href.includes('/followers/')) {
                            link.click();
                            return true;
                        }
                    }
                    return false;
                ''')
                time.sleep(3)
        except Exception as e:
            print(f"❌ Error al hacer clic en seguidores: {str(e)[:100]}")
            driver.save_screenshot("followers_button_error.png")
            print("📸 Captura de pantalla guardada como followers_button_error.png")
            return

        # Solución robusta para esperar el modal
        print("🔄 Esperando carga del modal de seguidores...")
        try:
            modal_xpaths = [
                #"//div[@role='dialog']",
                "//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6')]",
                "//div[contains(@class, 'x1ccrb07 xtf3nb5')]",
                "//div[contains(@class, 'x9f619')]//div[@role='dialog']"
            ]
            modal_found = False
            for xpath in modal_xpaths:
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    print(f"✅ Modal detectado con selector: {xpath}")
                    modal_found = True
                    break
                except:
                    continue
            if not modal_found:
                print("⚠️ Modal no detectado con selectores estándar")
                driver.save_screenshot("modal_not_found.png")
                print("📸 Captura de pantalla guardada como modal_not_found.png")
                print("🔄 Intentando método alternativo para detectar modal...")
                time.sleep(5)
                with open("instagram_debug.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("💾 HTML guardado para análisis en instagram_debug.html")
        except Exception as e:
            print(f"⚠️ Error detectando modal: {str(e)[:100]}")
            return

        # Desplazamiento mejorado en el modal
        print("📜 Comenzando desplazamiento en el modal...")
        try:
            scroll_xpaths = [
                "//div[@role='dialog']//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5')]",
                "//div[@role='dialog']//div[contains(@style, 'overflow')]"
            ]
            scrollable_div = None
            for xpath in scroll_xpaths:
                try:
                    scrollable_div = driver.find_element(By.XPATH, xpath)
                    print(f"✅ Área desplazable encontrada con selector: {xpath}")
                    break
                except:
                    continue
            if not scrollable_div:
                print("⚠️ No se encontró área desplazable específica, usando diálogo completo")
                scrollable_div = driver.find_element(By.XPATH, "//div[@role='dialog']")
            last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            scroll_attempts = 0
            max_attempts = 100000
            unique_elements = set()

            def count_followers():
                followers = driver.find_elements(By.XPATH,
                                                 "//div[@role='dialog']//a[contains(@href, '/') and not(contains(@href, 'explore'))]")
                usernames = set([follower.get_attribute("href").split("/")[-2]
                                 for follower in followers
                                 if follower.get_attribute("href")])
                return usernames

            scroll_pausa = random.randint(0, 2)
            while scroll_attempts < max_attempts:
                current_followers = count_followers()
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(random.uniform(1, 2))
                new_followers = count_followers()
                unique_elements.update(new_followers)
                print(
                    f"🔄 Scroll {scroll_attempts + 1}/{max_attempts} - Seguidores únicos: {len(unique_elements)} (+{len(new_followers - current_followers)} nuevos)"
                )
                if new_followers == current_followers:
                    scroll_pausa += 1
                    if scroll_pausa >= 3:
                        print("🔚 Fin del desplazamiento alcanzado - No hay más seguidores")
                        break
                else:
                    scroll_pausa = 0
                scroll_attempts += 1
                if scroll_attempts % 5 == 0:
                    time.sleep(random.uniform(5, 8))
        except Exception as e:
            print(f"⚠️ Error durante el desplazamiento: {str(e)[:100]}")

        # Extraer nombres de usuario de seguidores
        try:
            print("📝 Extrayendo seguidores...")
            follower_xpaths = [
                "//div[@role='dialog']//a[contains(@href, '/') and not(contains(@href, 'explore'))]",
                "//div[@role='dialog']//div[contains(@class, 'x9f619')]//a[contains(@href, '/')]",
                "//div[@role='dialog']//div[contains(@class, '_aacl')]//a"
            ]
            all_followers = []
            for xpath in follower_xpaths:
                followers = driver.find_elements(By.XPATH, xpath)
                all_followers.extend(followers)
            followers_usernames = []
            for follower in all_followers:
                href = follower.get_attribute("href")
                if href and "/p/" not in href and "/explore/" not in href:
                    username = href.split("/")[-2]
                    if username and username != "":
                        followers_usernames.append(username)
            followers_usernames = list(set(followers_usernames))
            print(f"✅ Total de seguidores únicos encontrados: {len(followers_usernames)}")
            if not followers_usernames:
                print("❌ No se encontraron seguidores")
                return
            with open("seguidores.txt", "w", encoding="utf-8") as f:
                for username in followers_usernames:
                    f.write(username + "\n")
            print("💾 Lista de seguidores guardada en seguidores.txt")
        except Exception as e:
            print(f"❌ Error extrayendo seguidores: {str(e)[:100]}")
            return

        # Extraer emails
        print("📧 Iniciando extracción de emails...")
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Username", "Email", "Profile URL"])
            processed = 0
            max_profiles = min(100, len(followers_usernames))
            for username in followers_usernames[:max_profiles]:
                try:
                    processed += 1
                    profile_url = f"https://www.instagram.com/{username}/"
                    print(f"\n👤 Perfil {processed}/{max_profiles}: {username}")
                    driver.get(profile_url)
                    time.sleep(random.uniform(4, 8))

                    # Intentar encontrar email en la biografía con múltiples métodos
                    email = None
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    bio_text = ""

                    # Método 1: Selectores específicos para la sección de bio
                    bio_selectors = [
                        "//section//h1/following-sibling::div/span",
                        "//div[contains(@class, 'x7a106z')]//span[contains(@class, 'x1lliihq')]",
                        "//div[contains(@class, '_aa_c')]//div[@class='_aacl _aacp _aacu _aacx _aad6 _aade']",
                        "//div[contains(@class, 'x9f619')]//div/span[@dir='auto']",
                        "//section//div/span[@dir='auto']"
                    ]
                    for selector in bio_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                bio_text += element.text + " "
                        except:
                            continue

                    # Metodo 2: Buscar la bio en todo el texto de la página
                    if not bio_text.strip():
                        bio_keywords = ["gmail.com", "@", "email", "contact", "contacto", "correo"]
                        for keyword in bio_keywords:
                            if keyword in page_text.lower():
                                start_idx = max(0, page_text.lower().find(keyword) - 50)
                                end_idx = min(len(page_text), page_text.lower().find(keyword) + 50)
                                context = page_text[start_idx:end_idx]
                                bio_text += context + " "

                    # Metodo 3: Analizar HTML directamente
                    '''if not bio_text.strip() or len(bio_text) < 20:
                        print("⚠️ Bio no encontrada con selectores XPath, buscando en HTML...")
                        page_source = driver.page_source
                        spans = re.findall(r'<span[^>]*>(.*?)</span>', page_source)
                        potential_bio = " ".join(
                            [span for span in spans if len(span) > 15 and not span.startswith("<")])
                        bio_text += potential_bio
                    '''
                    # Usar función mejorada de extracción de emails
                    email = extract_email_from_text(bio_text)
                    if not email:
                        email = extract_email_from_text(page_text)

                    # Si no está en la biografía, buscar botón de contacto
                    '''if not email:
                        try:
                            contact_xpaths = [
                                "//div[contains(text(), 'Contactar')]",
                                "//div[contains(text(), 'Email')]",
                                "//a[contains(@href, 'mailto:')]",
                                "//div[contains(@class, 'x9f619')]//div[contains(text(), 'Email')]"
                            ]
                            for xpath in contact_xpaths:
                                try:
                                    contact_elements = driver.find_elements(By.XPATH, xpath)
                                    for contact_element in contact_elements:
                                        driver.execute_script("arguments[0].click();", contact_element)
                                        time.sleep(random.uniform(2, 4))
                                        page_source = driver.page_source
                                        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                                                                page_source)
                                        if email_match:
                                            email = email_match.group(0)
                                            print(f"📩 Email encontrado en contacto: {email}")
                                            break
                                        driver.back()
                                        time.sleep(2)
                                except Exception as click_error:
                                    print(f"⚠️ Error al hacer clic en contacto: {str(click_error)[:30]}")
                                    continue
                        except Exception as contact_error:
                            print(f"⚠️ Error buscando contacto: {str(contact_error)[:30]}")
                        '''

                    # Buscar también en enlaces mailto:
                    '''if not email:
                        try:
                            mailto_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'mailto:')]")
                            if mailto_links:
                                href = mailto_links[0].get_attribute("href")
                                email = href.replace("mailto:", "").split("?")[0]
                                print(f"📩 Email encontrado en enlace mailto: {email}")
                        except:
                            pass'''

                    # Guardar resultados
                    if email:
                        writer.writerow([username, email, profile_url])
                        with open("emails_encontrados.txt", "a", encoding="utf-8") as f:
                            f.write(f"{username}: {email}\n")
                    else:
                        writer.writerow([username, "No encontrado", profile_url])
                        print("🔍 Email no encontrado")
                except Exception as e:
                    print(f"⚠️ Error procesando perfil {username}: {str(e)[:100]}...")
                    writer.writerow([username, f"Error: {str(e)[:50]}", profile_url, ""])
                if processed % 5 == 0:
                    time.sleep(random.uniform(5, 10))
                else:
                    time.sleep(random.uniform(5, 10))
        print(f"\n🎉 Proceso completado. Resultados guardados en {output_file}")
    except Exception as e:
        print(f"❌ Error crítico: {str(e)[:200]}")
        if driver:
            driver.save_screenshot("error_critico.png")
            print("📸 Captura de error guardada como error_critico.png")
    finally:
        if driver:
            driver.quit()
            print("🛑 Navegador cerrado")

if __name__ == "__main__":
    print("=== Instagram Follower Email Extractor ===")
    print("🔹 Versión mejorada con detección avanzada de emails")
    print("🔹 Uso educativo, cumple con políticas de Instagram\n")
    username = input("🔸 Tu usuario de Instagram: ")
    password = input("🔸 Tu contraseña: ")
    profile_url = input("🔸 URL del perfil a analizar (ej: https://www.instagram.com/usuario/): ").strip()
    chrome_path = input("🔸 Ruta completa al ejecutable de Chrome: ").strip()
    output_filename = "instagram_emails.csv"
    extract_instagram_emails(username, password, profile_url, chrome_path, output_filename)