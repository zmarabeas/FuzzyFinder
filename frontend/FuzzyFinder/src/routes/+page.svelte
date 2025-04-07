
<script>
  import VideoUploader from '$lib/components/VideoUploader.svelte';
  import VideoPlayer from '$lib/components/VideoPlayer.svelte';
  import { testServerFunction, testServerHealth } from '$lib/functions';
  import { FuzzyAPI } from '$lib/functions';
  import { onMount } from 'svelte';
  
  let videoFile = $state(null);
  let isVideoUploaded = $state(false);
  
  function handleFileUploaded(event) {
    videoFile = event.detail.file;
    isVideoUploaded = true;
  }
  
  function handleUploadNew() {
    videoFile = null;
    isVideoUploaded = false;
  }




  const api = new FuzzyAPI();
  onMount(async () => {
    const res = await testServerFunction();
    const health = await testServerHealth();
    console.log(await api.getAvailableDetectors());
    console.log(res);
    console.log(health);
  });
</script>

<main>
  <header>
    <div class="logo">
      <h1>Fuzzy Finder</h1>
      <p>PyTorch powered image classification</p>
    </div>
  </header>
  
  <section class="content">
    {#if !isVideoUploaded}
      <div class="upload-container">
        <VideoUploader fileUploaded={handleFileUploaded} />
      </div>
    {:else}
      <div class="video-player-container">
        <VideoPlayer videoFile={videoFile} />
        
        <div class="upload-new-container">
          <button class="upload-new-btn" onclick={handleUploadNew}>
            Upload New Video
          </button>
        </div>
      </div>
    {/if}
  </section>
  
  <footer>
    <p>Fuzzy Finder v0.0.1 &copy; 2025</p>
  </footer>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: #30292f; /* raisin-black */
    color: #ffffff;
  }
  
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  header {
    background-color: #413f54; /* english-violet */
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .logo h1 {
    margin: 0;
    font-size: 2rem;
    color: #ffffff;
    font-weight: 700;
  }
  
  .logo p {
    margin: 0.25rem 0 0;
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.8);
  }
  
  .content {
    flex: 1;
    padding: 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .upload-container {
    width: 100%;
    max-width: 800px;
  }
  
  .video-player-container {
    width: 100%;
    max-width: 800px;
    margin-bottom: 1.5rem;
  }
  
  /* VideoUploader styles */
  :global(.uploader-container) {
    background-color: #3f4045; /* onyx */
    border: 2px dashed rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 3rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative; /* Establish positioning context */
  }
  
  :global(.drag-active) {
    background-color: #413f54; /* english-violet */
    border-color: #5f5aa2; /* ultra-violet */
    transform: scale(1.01);
  }
  
  :global(.file-input) {
    display: none;
  }
  
  :global(.upload-content) {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    position: relative; /* For proper event bubbling */
    z-index: 1; /* Ensure content is above overlay */
    pointer-events: auto; /* Enable pointer events */
  }
  
  :global(.upload-icon) {
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 0.5rem;
  }
  
  :global(.upload-content h3) {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #ffffff;
  }
  
  :global(.upload-content p) {
    margin: 0;
    color: rgba(255, 255, 255, 0.7);
    max-width: 80%;
  }
  
  :global(.browse-btn) {
    margin-top: 1.5rem;
    background-color: #5f5aa2; /* ultra-violet */
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
    position: relative; /* For proper event bubbling */
    z-index: 1; /* Ensure button is above overlay */
  }
  
  :global(.browse-btn:hover) {
    background-color: #355691; /* yinmn-blue */
  }
  
  :global(.upload-progress-container) {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  :global(.progress-bar-container) {
    width: 100%;
    max-width: 300px;
    height: 8px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: hidden;
  }
  
  :global(.progress-bar) {
    height: 100%;
    background-color: #5f5aa2; /* ultra-violet */
    border-radius: 4px;
    transition: width 0.3s ease;
  }
  
  :global(.error-message) {
    color: #ff6b6b;
    background-color: rgba(255, 107, 107, 0.1);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    margin-top: 1rem;
    font-size: 0.875rem;
  }
  
  .upload-new-container {
    display: flex;
    justify-content: center;
  }
  
  .upload-new-btn {
    background-color: #5f5aa2; /* ultra-violet */
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  
  .upload-new-btn:hover {
    background-color: #355691; /* yinmn-blue */
  }
  
  footer {
    background-color: #413f54; /* english-violet */
    padding: 1rem;
    text-align: center;
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.6);
  }
</style>
