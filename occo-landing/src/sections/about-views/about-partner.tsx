"use client";
import { useState,useRef,useEffect } from "react";
import { useWindowSize } from "react-use";
import { Content } from "@/utils";
import Image from "next/image";
import partner from "../../../public/asset/images/partner4.png";
import partner1 from "../../../public/asset/images/parner1.png";
import partner2 from "../../../public/asset/images/parner3.png";
import AboutSwiper from "@/components/swiper/About-swiper";
//////
const part = [partner, partner1, partner2]; 
///
export default function AboutPartner() {
  const {width}=useWindowSize()
  let i = 0;
  let j = 0;
  const [scrollPosition, setScrollPosition] = useState(0);
  const [currentItem, setCurrentItem] = useState(0);
  const [divWidth, setDivWidth] = useState<number>(0);

  const divRef = useRef<HTMLDivElement>(null);


  const handleScroll = (event: React.UIEvent<HTMLDivElement>) => {
    const scrollLeft = event.currentTarget.scrollLeft;
    setScrollPosition(scrollLeft);
  };
  useEffect(()=>{
    if (divRef.current) {
      const width = divRef.current.clientWidth;
      setDivWidth(width);
    }


  },[width])

  return (
    <>
      <div className="  text-white max-w-screen min-w-screen 2xl:text-2xl lg:mt-10 max-lg:px-5 overflow-x-scroll no-scrollbar ">
        <div className=" flex flex-col justify-center gap-y-5">
          <div className="text-center text-[50px] pt-5 font-bold flex justify-center text-2xl max-sm:text-[22px] max-[736px]:text-[35px]  max-[500px]:px-5 min-[500px]:px-[80px] lg:text-[50px] sm:text-[30px] max-sm:text-[22px]">
            {Content.aboutContent.partner}
          </div>
          <div className="text-customGrey  flex justify-center ">
            <div style={{ marginBottom: '0px'}}  className="margin-top-text-partnet responsive-div lg:w-[960px] lg:h-[90px] text-center text-sm 2xl:text-xl max-sm:text-[14px] text-[18px] max-sm:w-[353px] max-sm:h-[87px] max-sm:leading-[22px] sm:leading-[34px] max-[500px]:px-5 min-[500px]:px-[80px] lg:text-[18px] sm:text-[16px] max-sm:text-[14px]">
              {Content.aboutContent.des}
            </div>
            <div></div>
          </div>
        </div>
        <div className="w-full flex justify-center lg:mt-10">
          <div className="lg:mx-[10%] max-w-[1440px] flex justify-center">
            <div className="grid grid-cols-3 gap-2 max-sm:hidden">
              {Content.aboutContent.card.map((item, index) => {
                return (
                  <div className="flex justify-center px-5" key={index}>
                    <div
                      className="flex justify-center w-[400px]  h-full min-h-[400px] lg:min-h-[500px]   py-10 flex-col gap-y-5 rounded-2xl"
                      style={{
                        backgroundImage:
                          "linear-gradient(to bottom, rgb(24 0 41) 0%, #2A0146 100%)",
                      }}
                    >
                      <div className="flex justify-center">
                        <Image src={part[i]} alt="" width={241} height={241}  className="max-[1220px]:w-[150px] max-[900px]:w-[100px] duration-100"/>
                        <div className="hidden">{i++} </div>
                      </div>
                      <div
                        className="flex justify-center font-bold lg:text-[30px] sm:text-[25px] max-sm:text-[22px] text-center duration-100"
                        style={{ color: "#7E21C8" }}
                      >
                        {item?.title}
                      </div>
                      <div className="flex justify-center text-center text-white lg:text-[20px] sm:text-[18px] max-sm:text-[16px] px-5 duration-100">
                        {item?.des}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        {/* <div> coroasle</div> */}
        <div className="flex justify-center pt-20 lg:hidden">
          <AboutSwiper/>
         
        </div>

      
      </div>
    </>
  );
}
