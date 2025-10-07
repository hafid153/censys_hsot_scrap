// index.js
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());

const COOKIE_PATH = path.resolve(__dirname, 'session_info/cookies.json');
const OUT_TXT = path.resolve(__dirname, 'data/page_text.txt');
const OUT_HTML = path.resolve(__dirname, 'session_info/page_dump.html');
const SCREENSHOT = path.resolve(__dirname, 'session_info/page_debug.png');

// check if subfolders exist or create it 
const dataFolder = path.resolve(__dirname, 'data');
const sessionFolder = path.resolve(__dirname, 'session_info');

if (!fs.existsSync(dataFolder)) {
  fs.mkdirSync(dataFolder, { recursive: true });
  console.log('Dossier data créé');
}

if (!fs.existsSync(sessionFolder)) {
  fs.mkdirSync(sessionFolder, { recursive: true });
  console.log('Dossier session_info créé');
}

const argv = process.argv.slice(2);
const URL = argv.find(a => !a.startsWith('--')) || 'https://example.com';
const FORCE = argv.includes('--force');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');
  await page.setViewport({ width: 1366, height: 768 });

  // Charger cookies si existants
  if (fs.existsSync(COOKIE_PATH)) {
    try {
      const cookies = JSON.parse(fs.readFileSync(COOKIE_PATH, 'utf8'));
      if (Array.isArray(cookies) && cookies.length) {
        await page.setCookie(...cookies);
        console.log(`✅ ${cookies.length} cookie(s) chargés  `);
      }
    } catch (e) {
      console.warn('⚠️ Impossible de lire cookies.json :', e.message);
    }
  }

  try {
    console.log(`⏳ Navigation vers l'url`);
    await page.goto(URL, { waitUntil: 'networkidle2', timeout: 60000 });
    // comportements "humains" simples
    try { await page.mouse.move(100,100); } catch(e) {}
    await page.evaluate(() => window.scrollTo(0, 200));
    await sleep(2000);

    // meilleure détection : on recherche des widgets visibles liés aux CAPTCHA / turnstile
    const captchaInfo = await page.evaluate(() => {
      const infos = { found: false, matches: [] };

      function isVisible(el) {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        if (!style) return false;
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        return true;
      }

      // 1) iframes (recaptcha often in iframe)
      const iframes = Array.from(document.querySelectorAll('iframe'));
      for (const fr of iframes) {
        const src = fr.getAttribute('src') || '';
        if (/recaptcha|google.com\/recaptcha|hcaptcha|turnstile|cloudflare/i.test(src) && isVisible(fr)) {
          infos.found = true;
          infos.matches.push({ type: 'iframe', src: src.slice(0,200) });
        }
      }

      // 2) elements classiques: divs with class names
      const selectors = [
        '[class*="captcha"]',
        '[id*="captcha"]',
        '[class*="g-recaptcha"]',
        '.h-captcha',
        '.cf-turnstile',
        '[data-sitekey]'
      ];
      const nodes = new Set();
      selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(n => nodes.add(n));
      });
      nodes.forEach(n => {
        if (isVisible(n)) {
          infos.found = true;
          infos.matches.push({ type: 'element', outer: n.outerHTML.slice(0,300) });
        }
      });

      // 3) hidden inputs used by some protections
      const hiddenInputs = Array.from(document.querySelectorAll('input[name="g-recaptcha-response"], textarea[name="h-captcha-response"]'));
      for (const hi of hiddenInputs) {
        if (isVisible(hi) || hi.value) {
          infos.found = true;
          infos.matches.push({ type: 'input', name: hi.getAttribute('name') });
        }
      }

      // 4) Cloudflare UAM indicators in DOM
      if (document.querySelector('#cf-content, .cf-browser-verification')) {
        infos.found = true;
        infos.matches.push({ type: 'cloudflare-uam' });
      }

      return infos;
    });

    if (captchaInfo.found) {
      console.error('⛔ Détection CAPTCHA/turnstile/recaptcha détectée :');
      console.error(JSON.stringify(captchaInfo.matches, null, 2));
      // snapshot & dump HTML pour debug
      await page.screenshot({ path: SCREENSHOT, fullPage: true }).catch(()=>{});
      const rawHtml = await page.content();
      fs.writeFileSync(OUT_HTML, rawHtml, 'utf8');

      if (!FORCE) {
        console.error(`Arrêt (utilise --force pour continuer malgré la détection). Screenshot: ${SCREENSHOT}, HTML: ${OUT_HTML}`);
        await browser.close();
        process.exit(2);
      } else {
        console.warn('⚠️ --force spécifié : on continue malgré la détection (attention, les résultats peuvent être incomplets).');
      }
    } else {
      console.log('✅ Aucune signature CAPTCHA visible détectée (détection DOM).');
    }

    // attendre un peu pour que le contenu dynamique se charge
    await sleep(3000);

    // Récupérer le texte visible (comme avant)
    const visibleText = await page.evaluate(() => {
      const toRemove = Array.from(document.querySelectorAll('script, style, noscript, template'));
      toRemove.forEach(el => el.remove());
      function getVisibleText(root = document.body) {
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
          acceptNode(node) {
            if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
            const parent = node.parentElement;
            if (!parent) return NodeFilter.FILTER_REJECT;
            const style = window.getComputedStyle(parent);
            if (style && (style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0')) {
              return NodeFilter.FILTER_REJECT;
            }
            return NodeFilter.FILTER_ACCEPT;
          }
        });
        let text = '';
        let cur;
        while (cur = walker.nextNode()) {
          text += cur.nodeValue.trim() + '\n';
        }
        return text.trim();
      }
      return getVisibleText();
    });

    // Toujours sauvegarder le texte visible dans page_text.txt (silencieux — ne pas écrire sur stdout)
    try {
      fs.writeFileSync(OUT_TXT, visibleText || '', 'utf8');
      console.log(`✅ Texte sauvegardé dans ${OUT_TXT}`);
    } catch (e) {
      console.error('⚠️ erreur écriture txt', e && e.message ? e.message : e);
    }

    if (!visibleText || !visibleText.length) {
      console.error('(aucun texte détecté — la page est peut-être très dynamique)');
    }

    const newCookies = await page.cookies();
    try { fs.writeFileSync(COOKIE_PATH, JSON.stringify(newCookies, null, 2)); console.log(`✅ Cookies sauvegardés dans ${COOKIE_PATH}`); } catch(e){ console.log('⚠️ erreur sauvegarde cookies', e.message); }

  } catch (err) {
    console.error('Erreur lors de la navigation :', err && err.message ? err.message : err);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
