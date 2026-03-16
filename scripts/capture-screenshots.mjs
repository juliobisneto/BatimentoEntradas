/**
 * Captura screenshots de cada tela do sistema.
 * Requer: app rodando em http://localhost:3000 e API em http://localhost:8000
 * Execute: node scripts/capture-screenshots.mjs
 */

import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import { join } from 'path';

const BASE_URL = 'http://localhost:3000';
const OUTPUT_DIR = join(process.cwd(), 'screenshots');
const LOGIN_EMAIL = 'admin@admin.com';
const LOGIN_PASSWORD = 'admin';

async function captureScreenshots() {
  await mkdir(OUTPUT_DIR, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    ignoreHTTPSErrors: true,
  });
  const page = await context.newPage();

  try {
    console.log('Abrindo aplicação...');
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 15000 });

    // 1. Tela de Login
    console.log('Capturando: Login');
    await page.screenshot({ path: join(OUTPUT_DIR, '01-login.png'), fullPage: true });

    // Fazer login
    console.log('Fazendo login...');
    await page.fill('input[type="email"]', LOGIN_EMAIL);
    await page.fill('input[type="password"]', LOGIN_PASSWORD);
    await page.click('button[type="submit"]');
    // Esperar carregar após login (header com título ou menu)
    await page.waitForTimeout(4000);

    // 2. Dashboard
    console.log('Capturando: Dashboard');
    await page.screenshot({ path: join(OUTPUT_DIR, '02-dashboard.png'), fullPage: true });

    // Garantir que o topo da página (menu) está visível
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(500);

    // Helper para clicar no menu (via JS para garantir compatibilidade)
    const clickNav = async (text) => {
      await page.evaluate((t) => {
        const buttons = [...document.querySelectorAll('button')];
        const btn = buttons.find((b) => b.textContent.trim() === t);
        if (btn) btn.click();
      }, text);
      await page.waitForTimeout(1500);
    };

    // 3. Payment Calendar
    console.log('Capturando: Payment Calendar');
    await clickNav('Payment Calendar');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: join(OUTPUT_DIR, '03-payment-calendar.png'), fullPage: true });

    // 4. File Import
    console.log('Capturando: File Import');
    await clickNav('File Import');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: join(OUTPUT_DIR, '04-file-import.png'), fullPage: true });

    // 5. Payment Methods
    console.log('Capturando: Payment Methods');
    await clickNav('Payment Methods');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: join(OUTPUT_DIR, '05-payment-methods.png'), fullPage: true });

    console.log('\nConcluído! Screenshots salvos em:', OUTPUT_DIR);
    console.log('  - 01-login.png');
    console.log('  - 02-dashboard.png');
    console.log('  - 03-payment-calendar.png');
    console.log('  - 04-file-import.png');
    console.log('  - 05-payment-methods.png');
  } catch (err) {
    console.error('Erro:', err.message);
    throw err;
  } finally {
    await browser.close();
  }
}

captureScreenshots();
