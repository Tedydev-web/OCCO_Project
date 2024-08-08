import LandingHero from "./landing-hero"
import LandingFeature from "./landing-feature"
import LandingGroup from "./landing-group"
import LandingSharing from "./landing-sharing"
import LandingFooter from "./landing-footer"
import HomeSwiper from "@/components/swiper/Home-swiper"
import { ToastContainer } from "react-toastify"
import 'react-toastify/dist/ReactToastify.css';

export default function LandingView(){
    return (<>
    {/* <ToastContainer /> */}

     <LandingHero/>

     <LandingFeature/>

     <LandingGroup/>

     <LandingSharing/>

     <LandingFooter/>

   

   
    </>)
}