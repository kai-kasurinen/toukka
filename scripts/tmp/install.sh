#!/bin/bash
# Gemini generoi keskustelun pohjalta. Ei varmaa toimiva, mutta dokumentaatioksi ehkä...

# Asetukset: Skripti lopettaa suorituksen heti, jos jokin komento epäonnistuu.
set -e

echo "Aloitetaan Toukka-projektin asennus..."

# 1. Tarkista ja asenna järjestelmätason riippuvuudet (esim. Python, pip, venv)
# Tämä osa voi vaihdella käyttöjärjestelmän mukaan.
# Oletetaan, että Python 3 ja pip ovat jo asennettuina tai asennetaan manuaalisesti.
# Esim. Debian/Ubuntu: sudo apt update && sudo apt install python3 python3-pip python3-venv

echo "Tarkistetaan Python 3 ja pip..."
if ! command -v python3 &> /dev/null
then
    echo "Virhe: Python 3 ei ole asennettu. Asenna se ensin (esim. 'sudo apt install python3')."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "Virhe: pip3 ei ole asennettu. Asenna se ensin (esim. 'sudo apt install python3-pip')."
    exit 1
fi

# 2. Luo ja aktivoi virtuaaliympäristö
VENV_DIR=".venv"
echo "Luodaan virtuaaliympäristö hakemistoon ${VENV_DIR}..."
python3 -m venv "${VENV_DIR}"

echo "Aktivoidaan virtuaaliympäristö..."
source "${VENV_DIR}/bin/activate"

# 3. Asenna Python-riippuvuudet
echo "Asennetaan Python-riippuvuudet (httpx, hishel, SQLAlchemy, xdg, jne.)..."
# Lisää tähän kaikki projektisi riippuvuudet
pip install --upgrade pip
pip install httpx hishel SQLAlchemy xdg psycopg2-binary # Lisää psycopg2-binary, jos käytät PostgreSQL:ää
# Jos sinulla on requirements.txt-tiedosto, voit käyttää:
# pip install -r requirements.txt

echo "Python-riippuvuudet asennettu."

# 4. Luo tietokantataulut
# Oletetaan, että sinulla on Python-skripti, joka hoitaa taulujen luomisen.
# Esimerkiksi aiemmin keskusteltu create_db.py tai SpotifyMprisHistoryDB:n __init__-metodi.
# Jos käytät SpotifyMprisHistoryDB:n __init__-metodia, sinun täytyy instansioida se.
# Tässä esimerkissä oletetaan, että sinulla on erillinen skripti 'create_db.py'
# tai vastaava komento, joka alustaa tietokannan.

echo "Luodaan tietokantataulut..."
# TÄMÄ KOHTA ON PROJEKTIKOHTAINEN!
# Jos sinulla on erillinen 'create_db.py' -skripti:
# python3 create_db.py

# Jos taulut luodaan SpotifyMprisHistoryDB-luokan instansioinnin yhteydessä:
# Sinun täytyy tuoda tarvittavat moduulit ja kutsua luokkaa.
# Esimerkki (polut voivat vaihdella):
python3 -c "import os; from toukka.sopiva.spotify_database.util import get_database_uri_from_config; from toukka.sopiva.spotify_mpris_history.database.current import SpotifyMprisHistoryDB; database_uri = get_database_uri_from_config(); expanded_uri = database_uri.replace('~', os.path.expanduser('~')) if '~' in database_uri else database_uri; print(f'Alustetaan SpotifyMprisHistoryDB URI:lla: {expanded_uri}'); SpotifyMprisHistoryDB(expanded_uri)"

echo "Tietokantataulut luotu (tai varmistettu)."

# 5. Luo konfiguraatiotiedosto (jos sitä ei ole)
# Oletetaan, että konfiguraatiotiedosto on ~/.config/toukka/config.yaml
CONFIG_DIR="${HOME}/.config/toukka"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"

echo "Tarkistetaan konfiguraatiotiedosto ${CONFIG_FILE}..."
if [ ! -f "${CONFIG_FILE}" ]; then
    echo "Konfiguraatiotiedostoa ei löydy. Luodaan esimerkkikonfiguraatio..."
    mkdir -p "${CONFIG_DIR}"
    cat << EOF > "${CONFIG_FILE}"
# ~/.config/toukka/config.yaml
spotify_client_id: "OMA_CLIENT_ID"
spotify_client_secret: "OMA_CLIENT_SECRET"
spotify_redirect_uri: "http://localhost:8888/callback"
database_uri: "sqlite:///$(xdg-user-dir CACHE)/toukka/toukka.db" # Tai "sqlite:///~/path/to/toukka.db"
EOF
    echo "Esimerkkikonfiguraatio luotu tiedostoon ${CONFIG_FILE}."
    echo "MUISTA PÄIVITTÄÄ spotify_client_id, spotify_client_secret ja spotify_redirect_uri!"
else
    echo "Konfiguraatiotiedosto löytyy jo."
fi

# 6. Aseta shell-skripteille suoritusoikeudet
echo "Asetetaan suoritusoikeudet shell-skripteille..."
# Oletetaan, että shell-skriptit ovat scripts/play -hakemistossa
chmod +x scripts/play/* || true # '|| true' estää virheen, jos hakemistoa ei ole tai siellä ei ole tiedostoja
echo "Suoritusoikeudet asetettu."

echo "Asennus valmis! Voit nyt käyttää Toukka-sovellusta."
echo "Muista aktivoida virtuaaliympäristö tarvittaessa komennolla: source ${VENV_DIR}/bin/activate"
echo "Ja päivittää Spotify API-tunnukset tiedostoon ${CONFIG_FILE}"
