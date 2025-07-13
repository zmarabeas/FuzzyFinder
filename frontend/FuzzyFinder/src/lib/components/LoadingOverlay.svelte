<script>
  export let visible = false;
  export let message = 'Loading...';
</script>

{#if visible}
  <div class="overlay" role="alert" aria-live="assertive">
    <div class="spinner" aria-label="Loading"></div>
    <p>{message}</p>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    color: var(--color-text);
    backdrop-filter: blur(2px);
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  p {
    margin-top: 1rem;
    font-size: 1.25rem;
  }
</style>