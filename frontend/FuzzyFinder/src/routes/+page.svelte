<script>
  import VideoUploader from "$lib/components/VideoUploader.svelte";
  import VideoPlayer from "$lib/components/VideoPlayer.svelte";
  import ModelSelector from "$lib/components/ModelSelector.svelte";
  import LoadingOverlay from "$lib/components/LoadingOverlay.svelte";
  import { testServerFunction, testServerHealth } from "$lib/functions";
  import { FuzzyAPI } from "$lib/functions";
  import { onMount } from "svelte";

  let videoFile = $state(null);
  let isVideoUploaded = $state(false);
  let selectedModel = $state("yolo");
  let processingVideo = $state(false);
  let processedResults = $state(null);
  let processingError = $state(null);
  let showIntro = $state(true);

  const api = new FuzzyAPI();

  function handleFileUploaded(event) {
    videoFile = event.detail.file;
    isVideoUploaded = true;
    // Clear previous results when a new video is uploaded
    processedResults = null;
  }

  function handleUploadNew() {
    videoFile = null;
    isVideoUploaded = false;
    processedResults = null;
    processingError = null;
  }

  async function handleProcessVideo() {
    console.log("processing video with: ", selectedModel);
    processingVideo = true;
    processingError = null;

    try {
      const results = await api.processVideo(videoFile, selectedModel);
      console.log("Processing results:", results);
      processedResults = results;
    } catch (error) {
      console.error("Error processing video:", error);
      processingError = error.message || "Failed to process video";
    } finally {
      processingVideo = false;
    }
  }

  function navigateToApp() {
    showIntro = false;
  }

  onMount(async () => {
    // Test API connections
    try {
      const res = await testServerFunction();
      const health = await testServerHealth();
      const detectors = await api.getAvailableDetectors();
      console.log("API connection successful", { res, health, detectors });
    } catch (error) {
      console.error("API connection error:", error);
    }
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
    {#if showIntro}
      <div class="intro-container">
        <h2>Welcome to Fuzzy Finder</h2>
        <p>
          This application uses advanced computer vision models to detect and
          classify objects in videos. Simply upload a video, select a model, and
          let the magic happen!
        </p>
        <button class="get-started-btn" onclick={navigateToApp} aria-label="Get started">
          Get Started
        </button>
      </div>
    {:else}
      {#if !isVideoUploaded}
        <div class="upload-container">
          <VideoUploader fileUploaded={handleFileUploaded} />
        </div>
      {:else}
        <div class="video-player-container">
          <VideoPlayer
            {videoFile}
            animalSegments={processedResults?.animal_segments || []}
          />

          <div class="process-container">
            <div class="model-section">
              <ModelSelector bind:selectedModel />

              <button
                class="process-btn {processingVideo ? 'processing' : ''}"
                onclick={handleProcessVideo}
                disabled={processingVideo}
                aria-label="Process Video"
              >
                {#if processingVideo}
                  <span class="spinner-small"></span> Processing...
                {:else}
                  Process Video
                {/if}
              </button>
            </div>

            {#if processingError}
              <div class="error-message">
                {processingError}
              </div>
            {/if}

            {#if processedResults}
              <div class="results-summary">
                <h3>Processing Results</h3>
                <div class="results-stats">
                  <div class="stat">
                    <span class="stat-label">Detected Segments:</span>
                    <span class="stat-value"
                      >{processedResults.animal_segments.length}</span
                    >
                  </div>
                  <div class="stat">
                    <span class="stat-label">Detector:</span>
                    <span class="stat-value"
                      >{processedResults.metadata.detector}</span
                    >
                  </div>
                  <div class="stat">
                    <span class="stat-label">Video Duration:</span>
                    <span class="stat-value"
                      >{processedResults.metadata.duration.toFixed(2)}s</span
                    >
                  </div>
                  <div class="stat">
                    <span class="stat-label">Frames Processed:</span>
                    <span class="stat-value"
                      >{processedResults.frames.length}</span
                    >
                  </div>
                </div>
              </div>
            {/if}
          </div>

          <div class="divider"></div>

          <div class="upload-new-container">
            <button class="upload-new-btn" onclick={handleUploadNew} aria-label="Upload new video">
              Upload New Video
            </button>
          </div>
        </div>
      {/if}
    {/if}
  </section>

  <footer>
    <p>Fuzzy Finder v0.0.1 &copy; 2025</p>
  </footer>
  <LoadingOverlay visible={processingVideo} message="Processing video..." />
</main>

<style>
  :global(:root) {
    --color-bg: #30292f;
    --color-surface: #3f4045;
    --color-surface-alt: #413f54;
    --color-primary: #5f5aa2;
    --color-primary-hover: #355691;
    --color-text: #ffffff;
  }

  :global(body) {
    margin: 0;
    padding: 0;
    font-family:
      "Inter",
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      Roboto,
      Oxygen,
      Ubuntu,
      Cantarell,
      "Open Sans",
      "Helvetica Neue",
      sans-serif;
    background-color: var(--color-bg);
    color: var(--color-text);
  }

  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    background-color: var(--color-surface-alt);
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
    align-items: flex-start;
  }

  .intro-container {
    text-align: center;
    padding: 4rem 2rem;
    max-width: 800px;
    margin: 0 auto;
  }

  .intro-container h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: var(--color-text);
  }

  .intro-container p {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 2rem;
  }

  .get-started-btn {
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .get-started-btn:hover {
    background-color: var(--color-primary-hover);
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

  .process-container {
    margin-top: 20px;
    background-color: var(--color-surface);
    border-radius: 8px;
    padding: 16px;
  }

  .model-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
  }

  .process-btn {
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    height: 40px;
  }

  .process-btn:hover:not(:disabled) {
    background-color: var(--color-primary-hover);
  }

  .process-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .process-btn.processing {
    background-color: var(--color-surface-alt);
  }

  .spinner-small {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
  }

  .error-message {
    background-color: rgba(255, 99, 71, 0.2);
    color: #ff6347;
    padding: 12px;
    border-radius: 4px;
    margin-top: 12px;
    font-size: 14px;
  }

  .results-summary {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .results-summary h3 {
    margin: 0 0 12px 0;
    font-size: 16px;
    font-weight: 600;
  }

  .results-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
  }

  .stat {
    background-color: var(--color-surface-alt);
    padding: 12px;
    border-radius: 4px;
  }

  .stat-label {
    display: block;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 4px;
  }

  .stat-value {
    font-size: 16px;
    font-weight: 600;
  }

  .divider {
    height: 1px;
    background-color: rgba(255, 255, 255, 0.1);
    margin: 24px 0;
  }

  .upload-new-container {
    display: flex;
    justify-content: center;
  }

  .upload-new-btn {
    background-color: var(--color-primary);
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
    background-color: var(--color-primary-hover);
  }

  footer {
    background-color: var(--color-surface-alt);
    padding: 1rem;
    text-align: center;
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.6);
  }

  /* Add other styles from your original CSS here */

  @media (max-width: 640px) {
    .content {
      padding: 1rem;
    }

    .video-player-container,
    .upload-container {
      max-width: 100%;
    }
  }
</style>
