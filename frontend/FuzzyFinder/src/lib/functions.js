
async function testServerFunction() {
  const response = await fetch('http://localhost:5000/', {
    method: 'GET',
  });
  const data = await response.json();
  return data;
}

export { testServerFunction };
