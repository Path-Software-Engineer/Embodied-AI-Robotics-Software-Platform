import { expect, test } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('real simulator state, traced action and read-only replay are visible', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('status')).toContainText('LIVE SIMULATION', { timeout: 20_000 })
  await expect(page.getByRole('table').getByRole('row')).toHaveCount(4)
  await expect(page.getByRole('region', { name: 'Ciclo embodied observado' })).toContainText('completed')
  await expect(page.getByRole('combobox', { name: 'Run persistido' })).toHaveValue(/studio-/)
  await page.getByRole('button', { name: 'Cargar replay' }).click()
  await expect(page.getByRole('status')).toContainText('READ-ONLY REPLAY')
  await expect(page.getByRole('slider', { name: 'Muestra' })).toBeVisible()
  await expect(page.getByRole('combobox', { name: 'Velocidad' })).toHaveValue('1')
  await page.getByRole('combobox', { name: 'Velocidad' }).selectOption('2')
  await page.getByRole('button', { name: 'Reproducir' }).click()
  await expect(page.getByRole('button', { name: 'Pausar' })).toBeVisible()
  await page.getByRole('button', { name: 'Pausar' }).click()
  await page.getByRole('slider', { name: 'Muestra' }).fill('1')
  await expect(page.getByRole('region', { name: 'Ciclo embodied observado' })).toContainText('completed')
  await page.getByRole('button', { name: 'Volver a vivo' }).click()
  await expect(page.getByRole('status')).toContainText('LIVE SIMULATION')
})

test('keyboard access and explicit WebGL fallback preserve critical data', async ({ page }) => {
  await page.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
      if (type === 'webgl' || type === 'webgl2') return null
      return original.call(this, type, ...args)
    } as typeof HTMLCanvasElement.prototype.getContext
  })
  await page.goto('/')
  await expect(page.getByText('WebGL no disponible; datos accesibles en tabla.')).toBeVisible()
  await expect(page.getByRole('table').getByRole('row')).toHaveCount(4)
  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Cargar replay' })).toBeEnabled()
})

test('mobile observatory keeps table and replay controls available', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Simulation Observatory' })).toBeVisible()
  await expect(page.getByRole('table')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Cargar replay' })).toBeVisible()
})

test('automated accessibility audit has no serious or critical violations', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('status')).toContainText('LIVE SIMULATION', { timeout: 20_000 })
  const results = await new AxeBuilder({ page }).analyze()
  const blocking = results.violations.filter(item =>
    item.impact === 'serious' || item.impact === 'critical')
  expect(blocking).toEqual([])
})
