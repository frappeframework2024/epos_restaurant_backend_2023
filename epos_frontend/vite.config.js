import path from 'path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import proxyOptions from './proxyOptions';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [vue()],
	server: {
		port: 9999,
		proxy: proxyOptions,
		host:true
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src')
		}
	},
	build: {
		outDir: '../epos_restaurant_2023/public/epos_frontend',
		emptyOutDir: true,
		target: 'esnext'
		// target: 'es2015',
	}
});
