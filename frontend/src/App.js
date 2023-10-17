import React from 'react';
import { Route,Routes } from 'react-router-dom'
// import Navbar from './components/Navbar';
// import Bookchallan from './components/bookchallan'
import Home from './components/home'
import Register from './components/register'
import Offence from './components/offence'
import LoginPage from './components/login';
const App= ()=> {
    return (
      <>
      {/* <Navbar/> */}
      <Routes>
      <Route path='/' element={<LoginPage/>} />
      <Route path='/home' element={<Home/>} />
      <Route path='/register' element={<Register/>} />
      {/* <Route path='/book' element={<Bookchallan/>} /> */}
      <Route path='/offence/:_id/:proof' element={<Offence/>} />
      </Routes>
       </> 
    );
}

export default App;
