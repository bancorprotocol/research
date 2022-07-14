import React from 'react';
import Home from "./pages/home";
import Trading from "./pages/trading";
import Register from "./pages/register";
import Login from "./pages/login";
import RecoverPassword from "./pages/recover_password";
import ResetPassword from "./pages/reset_password";
import Faq from "./pages/faq";
import Grids from "./pages/sub/grids";
import Buttons from "./pages/sub/buttons";
import Tables from "./pages/sub/tables";
import Tabs from "./pages/sub/tabs";
import Pagination from "./pages/sub/pagination";
import FormsPage from "./pages/sub/forms_page";
import Marketcap from "./pages/marketcap";
import Ico from "./pages/ico";
import BuySell from "./pages/buy_sell";
import Wallet from "./pages/wallet";
import CurrencyExchange from "./pages/currency_exchange";
import Charts from "./pages/charts";
import FourZeroFour from "./pages/four_zero_four";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.min.css';
import "./assets/sass/main.scss";
import "./assets/css/shortcode.css";

function App() {
 
  return (
     <>
     <Router>
       <Switch>
         <Route path="/" exact>
            <Home />
         </Route>
         <Route path="/register" exact>
            <Register/>
         </Route>
         <Route path="/login" exact>
           <Login/>
         </Route>
         <Route path="/recover_password" exact>
            <RecoverPassword/>
         </Route>
         <Route path="/reset_password" exact>
            <ResetPassword/>
         </Route>
         <Route path="/trading" exact>
            <Trading/>
         </Route>
         <Route path="/faq" exact>
           <Faq/>
         </Route>
         <Route path="/grids" exact>
            <Grids/>
         </Route>
         <Route path="/buttons" exact>
            <Buttons/>
         </Route>
         <Route path="/tables" exact>
            <Tables/>
         </Route>
         <Route path="/tabs" exact>
            <Tabs/>
         </Route>
         <Route path="/pagination" exact>
            <Pagination/>
         </Route>
         <Route path="/forms" exact>
            <FormsPage/>
         </Route>
         <Route path="/marketcap" exact>
            <Marketcap/>
         </Route>
         <Route path="/ico" exact>
            <Ico/>
         </Route>
         <Route path="/buy_sell">
            <BuySell/>
         </Route>
         <Route path="/wallet">
            <Wallet/>
         </Route>
         <Route path="/charts">
            <Charts/>
         </Route>
         <Route path="/currency_exchange">
            <CurrencyExchange/>
         </Route>
          <Route path="*">
            <FourZeroFour />
          </Route>
       </Switch>
     </Router>
     </>
  );
}

export default App;
