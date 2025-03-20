<script>
  import { onMount } from 'svelte';
  import { testServerFunction } from '$lib/functions';

  onMount(async () => {
    const res = await testServerFunction();
    console.log(res);
  });

</script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://svelte.dev/docs/kit">svelte.dev/docs/kit</a> to read the documentation</p>
