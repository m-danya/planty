<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { initLocale, localizedError, t } from '$lib/i18n.svelte';

  let email = $state('');
  let password = $state('');
  let registration = $state(false);
  let loading = $state(false);
  let error = $state('');

  onMount(async () => {
    initLocale();
    try {
      await api.me();
      await goto('/');
    } catch {
      // Expected for a logged-out visitor.
    }
  });

  async function submit() {
    if (!email || !password || loading) return;
    loading = true;
    error = '';
    try {
      if (registration) await api.register(email, password);
      await api.login(email, password);
      await goto('/');
    } catch (reason) {
      error = reason instanceof ApiError
        ? (reason.status === 400 ? t('invalidCredentials') : localizedError(reason.message, t('serverUnavailable')))
        : t('serverUnavailable');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head><title>{registration ? t('registration') : t('signIn')} · Planty</title></svelte:head>

<main class="login-page">
  <section class="login-brand" aria-label="Planty">
    <div class="login-brand-content">
      <img src="/logo.png" alt="Planty" />
      <p>{t('brandLine')}</p>
    </div>
  </section>
  <section class="login-panel">
    <div class="login-card">
      <h1>{registration ? t('createAccount') : t('welcome')}</h1>
      <p class="login-subtitle">{registration ? t('registerSubtitle') : t('loginSubtitle')}</p>
      <form class="login-form" onsubmit={(event) => { event.preventDefault(); void submit(); }}>
        <label>{t('email')}<input type="email" bind:value={email} autocomplete="email" placeholder="user@example.ru" required /></label>
        <label>{t('password')}<input type="password" bind:value={password} autocomplete={registration ? 'new-password' : 'current-password'} minlength="8" required /></label>
        {#if error}<div class="form-error" role="alert">{error}</div>{/if}
        <button class="login-button" disabled={loading}>{loading ? t('wait') : registration ? t('register') : t('login')}</button>
      </form>
      <button class="signup-toggle" onclick={() => { registration = !registration; error = ''; }}>
        {registration ? t('haveAccount') : t('createAccount')}
      </button>
    </div>
  </section>
</main>
