
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
}

export { testServerHealth, testServerFunction};
