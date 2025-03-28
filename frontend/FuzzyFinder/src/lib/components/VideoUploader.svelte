
<script>
  // Svelte 5 syntax with callback props
  let { fileUploaded } = $props();
  
  let dragActive = $state(false);
  let fileInput;
  let uploadProgress = $state(0);
  let isUploading = $state(false);
  let uploadError = $state(null);
  
  function handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    dragActive = true;
  }
  
  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    // Only deactivate if leaving the parent container, not when moving between child elements
    if (e.currentTarget === e.target) {
      dragActive = false;
    }
  }
  
  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dragActive = true; // Ensure drag active state is maintained
  }
  
  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dragActive = false;
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }
  
  function handleFileInputChange(e) {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  }
  
  function handleFiles(files) {
    const file = files[0];
    const fileType = file.type;
    
    if (!fileType.startsWith('video/')) {
      uploadError = 'Please upload a valid video file.';
      return;
    }
    
    uploadError = null;
    simulateUpload(file);
  }
  
  function simulateUpload(file) {
    // This is a placeholder for the actual upload process
    // In a real app, you would use fetch or another method to upload to your backend
    isUploading = true;
    uploadProgress = 0;
    
    const interval = setInterval(() => {
      uploadProgress += 5;
      
      if (uploadProgress >= 100) {
        clearInterval(interval);
        isUploading = false;
        
        // Call the callback prop function with the file
        if (fileUploaded) {
          fileUploaded({ detail: { file } });
        }
      }
    }, 100);
  }
  
  function openFileSelector() {
    fileInput.click();
  }
</script>

<div 
  class="uploader-container"
  class:drag-active={dragActive}
  ondragenter={handleDragEnter}
  ondragleave={handleDragLeave}
  ondragover={handleDragOver}
  ondrop={handleDrop}
>
  <input
    type="file"
    accept="video/*"
    bind:this={fileInput}
    onchange={handleFileInputChange}
    class="file-input"
  />
  
  {#if isUploading}
    <div 
      class="upload-progress-container"
      ondragenter={handleDragEnter}
      ondragover={handleDragOver}
      ondrop={handleDrop}
    >
      <h3>Uploading video...</h3>
      <div class="progress-bar-container">
        <div class="progress-bar" style="width: {uploadProgress}%"></div>
      </div>
      <p>{uploadProgress}%</p>
    </div>
  {:else}
    <div 
      class="upload-content"
      ondragenter={handleDragEnter}
      ondragover={handleDragOver}
      ondrop={handleDrop}
    >
      <div class="upload-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      </div>
      <h3>Upload your video</h3>
      <p>Drag and drop your video file here or click to browse</p>
      
      {#if uploadError}
        <div class="error-message">
          {uploadError}
        </div>
      {/if}
      
      <button 
        class="browse-btn" 
        onclick={openFileSelector}
        ondragenter={handleDragEnter}
        ondragover={handleDragOver}
        ondrop={handleDrop}
      >
        Browse Files
      </button>
    </div>
  {/if}
</div>



<style>
  .uploader-container {
    background-color: #3f4045; /* onyx */
    border: 2px dashed rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 3rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .drag-active {
    background-color: #413f54; /* english-violet */
    border-color: #5f5aa2; /* ultra-violet */
    transform: scale(1.01);
  }
  
  .file-input {
    display: none;
  }
  
  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .upload-icon {
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 0.5rem;
  }
  
  h3 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #ffffff;
  }
  
  p {
    margin: 0;
    color: rgba(255, 255, 255, 0.7);
    max-width: 80%;
  }
  
  .browse-btn {
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
  }
  
  .browse-btn:hover {
    background-color: #355691; /* yinmn-blue */
  }
  
  .upload-progress-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .progress-bar-container {
    width: 100%;
    max-width: 300px;
    height: 8px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    background-color: #5f5aa2; /* ultra-violet */
    border-radius: 4px;
    transition: width 0.3s ease;
  }
  
  .error-message {
    color: #ff6b6b;
    background-color: rgba(255, 107, 107, 0.1);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    margin-top: 1rem;
    font-size: 0.875rem;
  }
</style>
