<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';

  let email = $state('');
  let password = $state('');
  let registration = $state(false);
  let loading = $state(false);
  let error = $state('');

  onMount(async () => {
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
        ? (reason.status === 400 ? 'Неверный email или пароль' : reason.message)
        : 'Не удалось связаться с сервером';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head><title>{registration ? 'Регистрация' : 'Вход'} · Planty</title></svelte:head>

<main class="login-page">
  <section class="login-brand" aria-label="Planty">
    <div class="login-brand-content">
      <img src="/logo.png" alt="Planty" />
      <p>Спокойное место для задач, планов и всего, что хочется успеть.</p>
    </div>
  </section>
  <section class="login-panel">
    <div class="login-card">
      <h1>{registration ? 'Создать аккаунт' : 'С возвращением'}</h1>
      <p class="login-subtitle">{registration ? 'Начните наводить порядок в делах' : 'Войдите, чтобы продолжить работу'}</p>
      <form class="login-form" onsubmit={(event) => { event.preventDefault(); void submit(); }}>
        <label>Email<input type="email" bind:value={email} autocomplete="email" placeholder="user@example.ru" required /></label>
        <label>Пароль<input type="password" bind:value={password} autocomplete={registration ? 'new-password' : 'current-password'} minlength="8" required /></label>
        {#if error}<div class="form-error" role="alert">{error}</div>{/if}
        <button class="login-button" disabled={loading}>{loading ? 'Подождите…' : registration ? 'Зарегистрироваться' : 'Войти'}</button>
      </form>
      <button class="signup-toggle" onclick={() => { registration = !registration; error = ''; }}>
        {registration ? 'У меня уже есть аккаунт' : 'Создать аккаунт'}
      </button>
    </div>
  </section>
</main>
