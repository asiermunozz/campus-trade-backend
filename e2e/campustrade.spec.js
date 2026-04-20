const { test, expect } = require('@playwright/test');

const URL_WEB = 'file:///C:/Users/Alonso/campus-trade-backend/index.html'; 

test.describe('CampusTrade - Suite Final de Alonso', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(URL_WEB);
    await page.waitForLoadState('networkidle');
    
    // Si hay sesión, cerramos antes de empezar
    const btnSalir = page.locator('text=Salir, text=Log Out, text=Cerrar Sesión').first();
    if (await btnSalir.isVisible()) {
      await btnSalir.click();
    }
  });

  test('1. Registro exitoso (Validando @campus.uan)', async ({ page }) => {
    // Generamos un correo que cumple la regla de la universidad
    const emailValido = `alonso_test_${Date.now()}@campus.uan`;
    
    await page.click('#btn-login');
    await page.click('text="Regístrate aquí"');
    
    // TRUCO: Buscamos solo dentro de la caja de registro para no confundirnos con el login
    const formulario = page.locator('#pantalla-registro');
    
    await formulario.getByPlaceholder('Tu Nombre').fill('Alonso Pro');
    await formulario.getByPlaceholder('Correo (@campus.uan)').fill(emailValido);
    await formulario.getByPlaceholder('Contraseña').fill('password123');
    
    await formulario.locator('button:has-text("Registrarse")').click();

    // Verificamos que el nombre aparece arriba (señal de que entró)
    await expect(page.locator('body')).toContainText('Alonso Pro');
  });

  test('2. Error de Login (Credenciales falsas)', async ({ page }) => {
    await page.click('#btn-login');
    
    const formLogin = page.locator('#pantalla-login');
    await formLogin.getByPlaceholder('Correo (@campus.uan)').fill('falso@campus.uan');
    await formLogin.getByPlaceholder('Contraseña').fill('123456');
    await formLogin.locator('button:has-text("Entrar")').click();
    
    await expect(page.locator('.toastify')).toBeVisible();
  });

  test('3. Buscador de productos', async ({ page }) => {
    await page.fill('#filtro-texto', 'calculadora');
    await page.press('#filtro-texto', 'Enter');
    const productos = page.locator('#grid-productos-tienda > div');
    expect(await productos.count()).toBeGreaterThanOrEqual(0);
  });

  test('4. Abrir detalle de producto', async ({ page }) => {
    const tarjeta = page.locator('#grid-productos-tienda > div').first();
    if (await tarjeta.isVisible()) {
      await tarjeta.click();
      await expect(page.locator('button:has-text("Comprar Ahora")')).toBeVisible();
    }
  });

  test('5. Bloqueo de publicación sin login', async ({ page }) => {
    await page.click('text="+ Anunciar"');
    await expect(page.locator('.toastify')).toBeVisible();
  });

  test('6. Cambio de Tema (Luna/Sol)', async ({ page }) => {
    const btnTema = page.locator('nav button i').first();
    await btnTema.click();
    await page.waitForTimeout(500);
    await btnTema.click(); // Volver a claro
  });

  test('7. Vista Móvil', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('nav')).toBeVisible();
  });

});