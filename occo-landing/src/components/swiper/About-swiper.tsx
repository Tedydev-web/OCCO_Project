"use client";

import React, { useRef, useState } from "react";
// Import Swiper React components
import { Swiper, SwiperSlide } from "swiper/react";

// Import Swiper styles
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import "./swiper.css"
import partner from "../../../public/asset/images/partner.png";
import partner1 from "../../../public/asset/images/parner1.png";
import partner2 from "../../../public/asset/images/parner3.png";
import Image from "next/image";
import { Autoplay, Pagination, Navigation } from 'swiper/modules';


import { Content } from "@/utils";

const part = [partner, partner1, partner2];

declare global {
  interface CSSStyleDeclaration {
    "--swiper-pagination-color"?: string;
    "--swiper-pagination-width"?: string;
    // Declare other custom CSS variables here...
  }
}

export default function AboutSwiper(){
    let i = 0;
    let j = 0;
    return (
    <>
    <div style={{ flexWrap: 'wrap', alignContent: 'space-around' }} className="flex justify-center w-full sm:hidden">
    <Swiper
        spaceBetween={30}
        centeredSlides={true}
        autoplay={{
          delay: 3000,
          disableOnInteraction: false,
        }}
        pagination={{
          clickable: true,
        }}
      
        modules={[Autoplay, Pagination, Navigation]}
        className="mySwiper h-[400px] flex justify-center"
       
      >
       
       
        {Content.aboutContent.card.map((item, index) => {
              return (
                <SwiperSlide className="flex"  key={index}>
                  <div style={{ alignContent: 'space-around'}} className="w-full flex justify-center">
                  <div
                    className="flex justify-center w-[310px] h-[353px]    flex-col gap-y-5 rounded-2xl carousel-item mx-2"
                    style={{
                      backgroundImage:
                        "linear-gradient(to bottom, rgb(24 0 41) 0%, #2A0146 100%)",
                    }}
                  >
                    <div className="w-full flex justify-center">
                    <div className="flex justify-center w-[136px] h-[136px]">
                      <Image src={part[j]} alt="" className="w-full" />
                      <div className="hidden">{j++} </div>
                    </div>
                    </div>
                    <div
                      className="flex justify-center font-bold text-2xl text-[22px] "
                      style={{ color: "#7E21C8" }}
                    >
                      {item?.title}
                    </div>
                   <div className="flex w-full justify-center">
                   <div className="flex justify-center text-center text-white text-xs text-[16px] w-[252px] h-[60px] ">
                      {item?.des}
                    </div>
                   </div>
                  </div>
                  </div>
                  </SwiperSlide>
              
              );
            })}
        
        {/* <SwiperSlide>Slide 2</SwiperSlide> */}
      
      </Swiper>
    </div>

    
    </>)
}