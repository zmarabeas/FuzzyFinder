<script>
  import { onMount } from 'svelte';
  import { FuzzyAPI } from '$lib/functions.js'

  // Define model options
  let models = [
    { id: 'resnet', name: 'ResNet (Image Classification)' },
    { id: 'yolo', name: 'YOLO (Fast Object Detection)' },
    { id: 'faster_rcnn', name: 'Faster R-CNN (Accurate Object Detection)' },
    { id: 'temporal_resnet', name: 'Temporal ResNet (with LSTM)' },
    { id: 'temporal_yolo', name: 'Temporal YOLO (with LSTM)' },
    { id: 'temporal_faster_rcnn', name: 'Temporal Faster R-CNN (with LSTM)' }
  ];

  // Selected model
  export let selectedModel = 'yolo';
  export let loading = false;

  const api = new FuzzyAPI();

  // Fetch available models from the API
  onMount(async () => {
    try {
      loading = true;
      const response = await api.getAvailableDetectors();
      
      if (response.ok) {
        const data = await response.json();
        
        // Update models list with what's available from the server
        models = data.detectors.map(id => {
          // Find existing model info if we have it
          const existingModel = models.find(m => m.id === id);
          
          if (existingModel) {
            return existingModel;
          } else {
            // Create a friendly name for any new models
            return {
              id,
              name: id.charAt(0).toUpperCase() + id.slice(1).replace(/_/g, ' ')
            };
          }
        });
        
        // Set default model
        if (data.default && !selectedModel) {
          selectedModel = data.default;
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    } finally {
      loading = false;
    }
  });

  // Handle model selection
  function handleModelChange(event) {
    selectedModel = event.target.value;
  }
</script>

<div class="model-selector">
  <label for="model-select">
    Animal Detection Model
    {#if loading}
      <span class="loading-indicator">Loading...</span>
    {/if}
  </label>
  
  <select
    id="model-select"
    bind:value={selectedModel}
    on:change={handleModelChange}
    disabled={loading}
  >
    {#each models as model}
      <option value={model.id}>
        {model.name}
      </option>
    {/each}
  </select>
  
  <div class="model-description">
    {#if selectedModel === 'resnet'}
      <p>ResNet50: General purpose image classifier. Good for simple scenes.</p>
    {:else if selectedModel === 'yolo'}
      <p>YOLO: Fast object detection that can identify multiple animals in a frame.</p>
    {:else if selectedModel === 'faster_rcnn'}
      <p>Faster R-CNN: More accurate object detection but slower than YOLO.</p>
    {:else if selectedModel === 'temporal_resnet'}
      <p>Temporal ResNet: Uses LSTM to analyze sequences of frames for better consistency.</p>
    {:else if selectedModel === 'temporal_yolo'}
      <p>Temporal YOLO: Fast detection with improved accuracy through temporal analysis.</p>
    {:else if selectedModel === 'temporal_faster_rcnn'}
      <p>Temporal Faster R-CNN: Most accurate detection with temporal consistency.</p>
    {:else}
      <p>Select a model to see its description.</p>
    {/if}
  </div>
</div>

<style>
  .model-selector {
    margin-bottom: 1.5rem;
    width: 100%;
  }

  label {
    display: flex;
    align-items: center;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .loading-indicator {
    font-size: 0.8rem;
    margin-left: 0.5rem;
    color: #666;
    font-style: italic;
  }

  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: white;
    font-size: 1rem;
    cursor: pointer;
  }

  select:focus {
    outline: none;
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
  }

  .model-description {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #555;
    background-color: #f5f5f5;
    padding: 0.75rem;
    border-radius: 4px;
    border-left: 3px solid #4299e1;
  }
</style>
