
const serverRoute = 'http://localhost:5005';

async function testServerFunction() {
  let route = '/';
  route = serverRoute + route;
  const response = await fetch(route, {
    method: 'GET',
  });
  const data = await response.json();
  return data;
}

async function testServerHealth(){
  let route = '/health'
  route = serverRoute + route;
  const response = await fetch(route, {
    method: 'GET',
  });
  const data = await response.json();
  return data;
}

async function getAvailableDetectors(){
  let route = '/health'
  route = serverRoute + route;
  const response = await fetch(route, {
    method: 'GET',
  });
  const data = await response.json();
  return data;
}

export class FuzzyAPI{
  r = 'http://localhost:5005';
  constructor(route){
    if(route)
      this._serverRoute = route; 
    else
      this._serverRoute = this.r;
  }

  get serverRoute(){
    return this._serverRoute;
  }

  set serverRoute(r){
    this._serverRoute = r;
  }


  async testServerFunction() {
    let route = '/';
    route = this.serverRoute + route;
    const response = await fetch(route, {
      method: 'GET',
    });
    const data = await response.json();
    return data;
  }

  async testServerHealth(){
    let route = '/health'
    route = this.serverRoute + route;
    const response = await fetch(route, {
      method: 'GET',
    });
    const data = await response.json();
    return data;
  }

  async getAvailableDetectors(){
    let route = '/available-detectors'
    route = this.serverRoute + route;
    const response = await fetch(route, {
      method: 'GET',
    });
    const data = await response.json();
    return data;
  }

  /**
   * Function to send a video file for animal detection processing
   * @param {File} videoFile - The video file to process
   * @param {string} detectorType - The type of detector to use (e.g., 'yolo', 'resnet', 'temporal_yolo')
   * @returns {Promise} - Promise that resolves with the processing results
   */
  async processVideo(videoFile, detectorType = 'yolo') {
    let route = '/process-video'
    route = this.serverRoute + route;


    // Create form data
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('detector', detectorType);
    
    try {
      // Make the request
      const response = await fetch(route, {
        method: 'POST',
        body: formData,
        // No need to set Content-Type header - fetch sets it automatically with boundary for FormData
      });
      
      // Check if the request was successful
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
      }
      
      // Parse and return the JSON response
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error processing video:', error);
      throw error;
    }
  }

  
}

export { testServerHealth, testServerFunction};
