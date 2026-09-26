import { expect, test } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('architecture cards link actual protocols, source hashes and residual risk', async ({ page }) => {
  await page.goto('/')
  const studio = page.getByRole('region', { name: 'Estudio de arquitectura' })
  await expect(studio.getByText('Architecture studio')).toBeVisible()
  await expect(studio.getByText('7', { exact: true }).first()).toBeVisible()
  await studio.getByRole('button', { name: /Independent C\+\+ simulation safety supervisor/ }).click()
  await expect(studio.getByText(/AuthorizeMotion.srv/)).toBeVisible()
  await expect(studio.getByText(/test_safety_rules.cpp/).first()).toBeVisible()
  await expect(studio).toContainText('ai-p64 · unavailable')
  await expect(studio).toContainText('not-measured')
  await expect(studio).toContainText('Simulation-only; no physical safety certification')
  await expect(studio).toContainText('Manifest SHA-256:')
  const manifest = await (await page.request.get('/api/v3/architecture/manifest')).json()
  const history = await (await page.request.get('/api/v3/architecture/snapshots')).json()
  expect(history.snapshots.some((item: { manifest_sha256: string }) => item.manifest_sha256 === manifest.manifest_sha256)).toBe(true)
  const android = await (await page.request.get('/api/v3/architecture/android-evidence')).json()
  expect(android.manifest_sha256).toBe(manifest.manifest_sha256)
  const accessibility = await new AxeBuilder({ page }).include('#architecture').analyze()
  expect(accessibility.violations).toEqual([])
})

test('architecture cards remain navigable on a narrow viewport', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 })
  await page.goto('/#architecture')
  const studio = page.getByRole('region', { name: 'Estudio de arquitectura' })
  await expect(studio.getByRole('button', { name: /Gazebo Sim studio/ })).toBeVisible()
  await studio.getByRole('button', { name: /Gazebo Sim studio/ }).click()
  await expect(studio.getByText('sim/worlds/studio.sdf')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375)
})
