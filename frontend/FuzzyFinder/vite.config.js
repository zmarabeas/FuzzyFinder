import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		environment: 'jsdom',
		globals: true,
		setupFiles: [],
		deps: {
			inline: ['@sveltejs/vite-plugin-svelte']
		},
		coverage: {
			reporter: ['text', 'html']
		}
	}
});
