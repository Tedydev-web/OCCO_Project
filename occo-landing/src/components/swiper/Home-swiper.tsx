"use client";

import React, { useRef, useState } from "react";
// Import Swiper React components
import { Swiper, SwiperSlide } from "swiper/react";

// Import Swiper styles
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import "./swiper.css"

import user from "../../../public/asset/images/user.png";
import heart from "../../../public/asset/images/heart.png";
import reta from "../../../public/asset/images/solar_widget-2-bold.png";
import location from "../../../public/asset/images/solar_map-point-favourite-bold.png";
import Image from "next/image";
import phone from "../../../public/asset/images/phone.png";


import { Content } from "@/utils";

// import required modules
import { Autoplay, Pagination, Navigation } from "swiper/modules";

declare global {
  interface CSSStyleDeclaration {
    "--swiper-pagination-color"?: string;
    "--swiper-pagination-width"?: string;
    // Declare other custom CSS variables here...
  }
}

const slideOption = [
  {
    name: "Chi tiết profile",
    des: "Nếu muốn biết thêm về đối phương, lướt lên để xem trang cá nhân.",
    image: user,
  },
  {
    name: Content.HomeContent.location,
    des: "Kết nối qua chia sẻ vị trí và gặp gỡ dễ dàng.",
    image: location,
  },
  {
    name: "Nhắn tin",
    des: "Dễ dàng gửi và nhận tin nhắn từ bạn bè và người thân.",
    image: heart,
  },
  {
    name: "Độ tương hợp",
    des: "Khám phá mức độ tương hợp giữa bạn và đối tác.",
    image: reta,
  },
];

export default function HomeSwiper() {
  return (
    // <>
     
     
     <div className="div pt-[30px] md:hidden">
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
        className="mySwiper pt- text-white pt-[20]   min-h-[170px]"
        
      >
        {
          slideOption.map((item, index) => {
            // console.log(item.name)
            return (
              // <>
                <SwiperSlide className="max-[500px]:px-5 min-[500px]:px-[80px]" key={index}>
                  <div className=" flex flex-col  w-full items-center">
                    <div className=" flex  justify-center">
                      <div className=" h-[34px] w-[34px] rounded-md bg-purple-700 flex items-center justify-center" style={{backgroundColor:' #A11BC7'}}>
                        <Image
                          src={item.image}
                          alt=""
                          width={17}
                          height={17}
                          quality={100}
                          className="max-h-[17px]"
                        />
                      </div>
                    </div>
                    <div className="py-2 flex  justify-center text-[18px]">
                      {item.name}
                    </div>
                    <div
                      className=" flex  justify-center text-sm w-full text-center text-[14px] h-full max-"
                      style={{ color: "#817DA0" }}
                    >
                      {item.des}
                    </div>
                  </div>
                </SwiperSlide>
              // </>
            );
          })}
      </Swiper>
     </div>
    // </>
  );
}
