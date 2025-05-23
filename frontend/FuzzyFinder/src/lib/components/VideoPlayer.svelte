<script>
  import { onDestroy } from "svelte";

  // Props
  let { videoFile, animalSegments = [] } = $props();

  // Fixed dimensions for the video player
  const playerWidth = 720;
  const playerHeight = 405;

  let videoElement;
  let videoUrl = $state("");
  let isPlaying = $state(false);
  let currentTime = $state(0);
  let duration = $state(0);
  let volume = $state(1);
  let isMuted = $state(false);
  let isFullscreen = $state(false);
  let isLoading = $state(true);
  let currentSegmentIndex = $state(-1);

  // Add multiple event listeners to ensure we catch the loading events
  $effect(() => {
    if (videoElement && videoUrl) {
      const handleLoaded = () => {
        console.log("Video loaded event fired");
        isLoading = false;
        if (videoElement.duration) {
          duration = videoElement.duration;
        }
      };

      videoElement.addEventListener("loadeddata", handleLoaded);
      videoElement.addEventListener("canplay", handleLoaded);

      return () => {
        videoElement.removeEventListener("loadeddata", handleLoaded);
        videoElement.removeEventListener("canplay", handleLoaded);
      };
    }
  });

  let isDraggingScrubber = $state(false);

  // Create an object URL when the video file changes
  $effect(() => {
    if (videoFile) {
      // Don't revoke in the effect, we'll do it in onDestroy
      // This fixes the infinite creation issue
      if (!videoUrl) {
        videoUrl = URL.createObjectURL(videoFile);
        videoElement.load();
        videoElement.controls = false;
        isLoading = true;

        // Debug logging
        console.log("Video URL created:", videoUrl);
        console.log("Video file:", videoFile);
        console.log("Video element: ", videoElement);

        // Some browsers may not trigger onloadedmetadata
        // Add a fallback timeout to hide loading after 2 seconds
        setTimeout(() => {
          if (isLoading) {
            console.log("Fallback: forcing loading complete");
            isLoading = false;

            // Try to get duration if available
            if (videoElement && videoElement.duration) {
              duration = videoElement.duration;
            }
          }
        }, 2000);
      }
    }
  });

  // Minimum segment duration in frames (assuming 30fps)
  const MIN_SEGMENT_FRAMES = 10;
  const MIN_SEGMENT_DURATION = MIN_SEGMENT_FRAMES / 30; // in seconds

  // Filter segments by minimum duration
  let filteredSegments = $derived(
    animalSegments.filter(
      (segment) => segment.end_time - segment.start_time >= MIN_SEGMENT_DURATION
    )
  );

  // Update current segment index whenever the current time changes
  $effect(() => {
    if (filteredSegments && filteredSegments.length > 0) {
      const foundIndex = filteredSegments.findIndex(
        (segment) =>
          currentTime >= segment.start_time && currentTime <= segment.end_time
      );

      currentSegmentIndex = foundIndex;
    }
  });

  // Handle play/pause
  function togglePlayPause() {
    if (videoElement.paused) {
      videoElement.play();
    } else {
      videoElement.pause();
    }
  }

  // Handle video metadata loaded
  function handleMetadataLoaded() {
    console.log("Metadata loaded, duration:", videoElement.duration);
    duration = videoElement.duration;
    isLoading = false;
  }

  // Update current time as video plays
  function handleTimeUpdate() {
    if (!isDraggingScrubber) {
      currentTime = videoElement.currentTime;
    }
  }

  // Handle video playing state
  function handlePlayState() {
    isPlaying = !videoElement.paused;
  }

  // Format time values (seconds -> MM:SS)
  function formatTime(timeInSeconds) {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }

  // Handle scrubber click/drag
  function handleScrubberClick(event) {
    const rect = event.currentTarget.getBoundingClientRect();
    const clickPosition = (event.clientX - rect.left) / rect.width;

    // Set video time based on click position
    videoElement.currentTime = clickPosition * duration;
    currentTime = videoElement.currentTime;
  }

  // Handle volume change
  function handleVolumeChange(event) {
    volume = parseFloat(event.target.value);
    videoElement.volume = volume;

    // Update mute state
    if (volume === 0) {
      isMuted = true;
    } else {
      isMuted = false;
    }
  }

  // Toggle mute
  function toggleMute() {
    isMuted = !isMuted;
    videoElement.muted = isMuted;
  }

  // Toggle fullscreen
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      videoElement.requestFullscreen();
      isFullscreen = true;
    } else {
      document.exitFullscreen();
      isFullscreen = false;
    }
  }

  // Move forward/backward by frames (approximate frame rate of 30fps)
  function moveFrame(direction) {
    const frameTime = 1 / 30; // 33.33ms
    videoElement.currentTime += direction * frameTime;
    currentTime = videoElement.currentTime;
  }

  // Jump to specific segment
  function jumpToSegment(index) {
    if (filteredSegments && filteredSegments[index]) {
      videoElement.currentTime = filteredSegments[index].start_time;
      currentTime = videoElement.currentTime;

      // Auto-play when jumping to segment
      // if (videoElement.paused) {
      //   videoElement.play();
      // }
    }
  }

  // Jump to next/previous segment
  function navigateSegments(direction) {
    let targetIndex;

    if (currentSegmentIndex === -1) {
      // If not in a segment, find the nearest one
      if (direction > 0) {
        // Find next segment
        const nextSegment = filteredSegments.find(
          (segment) => segment.start_time > currentTime
        );
        targetIndex = nextSegment ? filteredSegments.indexOf(nextSegment) : 0;
      } else {
        // Find previous segment
        const prevSegments = filteredSegments.filter(
          (segment) => segment.end_time < currentTime
        );
        targetIndex =
          prevSegments.length > 0
            ? filteredSegments.indexOf(prevSegments[prevSegments.length - 1])
            : filteredSegments.length - 1;
      }
    } else {
      // If in a segment, go to next/previous
      targetIndex =
        (currentSegmentIndex + direction + filteredSegments.length) %
        filteredSegments.length;
    }

    jumpToSegment(targetIndex);
  }

  // Cleanup when component is destroyed
  onDestroy(() => {
    console.log("player destroyed");
    if (videoUrl) {
      console.log("removing url", videoUrl);
      URL.revokeObjectURL(videoUrl);
    }
  });
</script>

<div class="video-player-container">
  <div
    class="video-player"
    style="width: {playerWidth}px; height: {playerHeight}px;"
  >
    {#if isLoading}
      <div class="loading-overlay">
        <div class="spinner"></div>
        <p>Loading video...</p>
      </div>
    {/if}

    <video
      bind:this={videoElement}
      src={videoUrl}
      onloadedmetadata={handleMetadataLoaded}
      ontimeupdate={handleTimeUpdate}
      onplay={handlePlayState}
      onpause={handlePlayState}
      onclick={togglePlayPause}
      style="object-fit: contain;"
    ></video>

    <div class="controls">
      <div class="scrubber-container" onclick={handleScrubberClick}>
        <div class="scrubber-track">
          <div
            class="scrubber-progress"
            style="width: {(currentTime / duration) * 100}%"
          ></div>

          {#if filteredSegments && filteredSegments.length > 0}
            {#each filteredSegments as segment, index}
              <div
                class="segment-marker"
                style="left: {(segment.start_time / duration) *
                  100}%; width: {((segment.end_time - segment.start_time) /
                  duration) *
                  100}%;"
                title="Animal segment #{index + 1}: {formatTime(
                  segment.start_time
                )} - {formatTime(segment.end_time)} ({(
                  (segment.end_time - segment.start_time) *
                  30
                ).toFixed(0)} frames)"
              ></div>
            {/each}
          {/if}
        </div>
        <div
          class="scrubber-handle"
          style="left: {(currentTime / duration) * 100}%"
        ></div>
      </div>

      <div class="controls-bottom">
        <div class="left-controls">
          <button class="control-button" onclick={togglePlayPause}>
            {#if isPlaying}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
              </svg>
            {:else}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            {/if}
          </button>

          <button class="control-button" onclick={() => moveFrame(-1)}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="11 17 6 12 11 7"></polyline>
            </svg>
          </button>

          <button class="control-button" onclick={() => moveFrame(1)}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="13 17 18 12 13 7"></polyline>
            </svg>
          </button>

          <div class="time-display">
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>
        </div>

        <div class="right-controls">
          <div class="volume-control">
            <button class="control-button" onclick={toggleMute}>
              {#if isMuted || volume === 0}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                  <path
                    d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"
                  ></path>
                  <path
                    d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"
                  ></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
              {:else}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
                  <path
                    d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"
                  ></path>
                </svg>
              {/if}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onchange={handleVolumeChange}
              oninput={handleVolumeChange}
            />
          </div>

          <button class="control-button" onclick={toggleFullscreen}>
            {#if isFullscreen}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"
                ></path>
              </svg>
            {:else}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"></path>
              </svg>
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>

  {#if filteredSegments && filteredSegments.length > 0}
    <div class="segment-navigation" style="width: {playerWidth}px;">
      <h3>
        Animal Segments ({filteredSegments.length} segments, min {MIN_SEGMENT_FRAMES}
        frames)
      </h3>

      <div class="segment-controls">
        <button class="segment-nav-button" onclick={() => navigateSegments(-1)}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M19 12H5M12 19l-7-7 7-7"></path>
          </svg>
          Previous
        </button>

        <button class="segment-nav-button" onclick={() => navigateSegments(1)}>
          Next
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </button>
      </div>

      <div class="segment-list">
        {#each filteredSegments as segment, index}
          <button
            class="segment-button {currentSegmentIndex === index
              ? 'active'
              : ''}"
            onclick={() => jumpToSegment(index)}
          >
            <span class="segment-number">{index + 1}</span>
            <span class="segment-time"
              >{formatTime(segment.start_time)} - {formatTime(
                segment.end_time
              )}</span
            >
            <span class="segment-duration">
              ({(segment.end_time - segment.start_time).toFixed(1)}s /
              {((segment.end_time - segment.start_time) * 30).toFixed(0)} frames)
            </span>
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .video-player-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: fit-content;
    margin: 0 auto;
  }

  .video-player {
    position: relative;
    background-color: #000;
    border-radius: 8px;
    overflow: hidden;
    margin: 0 auto;
  }

  video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background-color: #000;
    display: block;
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 2;
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #5f5aa2;
    animation: spin 1s ease-in-out infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .loading-overlay p {
    color: white;
    margin-top: 12px;
    font-size: 16px;
  }

  .controls {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 8px;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .video-player:hover .controls {
    opacity: 1;
  }

  .scrubber-container {
    position: relative;
    height: 18px;
    margin-bottom: 8px;
    cursor: pointer;
  }

  .scrubber-track {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 100%;
    height: 4px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
  }

  .scrubber-progress {
    height: 100%;
    background-color: #5f5aa2;
    border-radius: 2px;
  }

  .segment-marker {
    position: absolute;
    height: 6px;
    top: 6px;
    background-color: #ff8600;
    border-radius: 2px;
    z-index: 1;
    opacity: 0.8;
    pointer-events: none;
  }

  .scrubber-handle {
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 12px;
    height: 12px;
    background-color: #5f5aa2;
    border-radius: 50%;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
    z-index: 3;
  }

  .controls-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .left-controls,
  .right-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .control-button {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    width: 32px;
    height: 32px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .control-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .time-display {
    color: white;
    font-size: 14px;
    min-width: 100px;
  }

  .volume-control {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  input[type="range"] {
    width: 80px;
    height: 4px;
    -webkit-appearance: none;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    outline: none;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
  }

  input[type="range"]::-moz-range-thumb {
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }

  /* Animal Segment Navigation */
  .segment-navigation {
    background-color: #413f54;
    border-radius: 0 0 8px 8px;
    padding: 16px;
    margin-top: 4px;
  }

  .segment-navigation h3 {
    margin: 0 0 12px 0;
    font-size: 16px;
    color: white;
    font-weight: 600;
  }

  .segment-controls {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .segment-nav-button {
    display: flex;
    align-items: center;
    gap: 6px;
    background-color: #5f5aa2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .segment-nav-button:hover {
    background-color: #355691;
  }

  .segment-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 8px;
    max-height: 200px;
    overflow-y: auto;
    padding-right: 4px;
  }

  .segment-button {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #3f4045;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    text-align: left;
    cursor: pointer;
    transition: background-color 0.2s;
    font-size: 14px;
  }

  .segment-button:hover {
    background-color: #5f5aa2;
  }

  .segment-button.active {
    background-color: #ff8600;
    font-weight: 500;
  }

  .segment-number {
    background-color: rgba(255, 255, 255, 0.2);
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
  }

  .segment-time {
    flex-grow: 1;
  }

  .segment-duration {
    font-size: 12px;
    opacity: 0.7;
  }

  /* Scrollbar styling for segment list */
  .segment-list::-webkit-scrollbar {
    width: 6px;
  }

  .segment-list::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }

  .segment-list::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
  }

  .segment-list::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }
</style>
