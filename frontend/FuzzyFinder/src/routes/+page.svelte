<!--
  import { testServerFunction } from '$lib/functions';

  {/* onMount(async () => { */}
  {/*   const res = await testServerFunction(); */}
  {/*   console.log(res); */}
  {/* }); */}
-->

<script>
  import VideoUploader from '$lib/components/VideoUploader.svelte';
  
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
        <div class="player-placeholder">
          <!-- Video player component will go here -->
          <div class="placeholder-text">
            <h3>Video Player</h3>
            <p>Filename: {videoFile.name}</p>
          </div>
        </div>
        
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
  }
  
  .player-placeholder {
    background-color: #3f4045; /* onyx */
    border-radius: 8px;
    height: 450px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  
  .placeholder-text {
    text-align: center;
    color: rgba(255, 255, 255, 0.7);
  }
  
  .placeholder-text h3 {
    margin: 0 0 0.5rem;
    font-size: 1.5rem;
  }
  
  .placeholder-text p {
    margin: 0;
    font-size: 1rem;
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
