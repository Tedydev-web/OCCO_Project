"use client";

////@hooks
import { useState, useRef, useEffect } from "react";
import { useWindowSize } from "react-use";

///assets
import Image from "next/image";
import phone from "../../../public/asset/images/phone.png";
import a from "../../../public/asset/images/lover.png";
import group_1 from "../../../public/asset/images/hinh1.png";
import user from "../../../public/asset/images/user.png";
import heart from "../../../public/asset/images/heart.png";
import reta from "../../../public/asset/images/solar_widget-2-bold.png";
import location from "../../../public/asset/images/location.png";
import HomeSwiper from "@/components/swiper/Home-swiper";

import { Content } from "@/utils";

export default function LandingGroup() {
  const { width } = useWindowSize();
  const divRef = useRef<HTMLDivElement>(null);
  const divRef2 = useRef<HTMLDivElement>(null);

  const [currentItem, setCurrentItem] = useState(0);
  const [divWidth, setDivWidth] = useState<number>(0);
  const [divWidthb, setDivWidthb] = useState<number | null>(0);
  const [scrollPosition, setScrollPosition] = useState(0);

  const handleScroll = (event: React.UIEvent<HTMLDivElement>) => {
    const scrollLeft = event.currentTarget.scrollLeft;
    setScrollPosition(scrollLeft);
  };

  useEffect(() => {
    if (divRef.current) {
      const width = divRef.current.clientWidth;
      const width2 = divRef.current.clientWidth;
      setDivWidthb(width2);
      setDivWidth(width);
    }
  }, [width]);

  return (
    <>
      {/* { mobile screen} */}
     
      <div className=" max-h-max	2xl:text-2xl  pt-10 px-10 text-white flex justify-center items-center md:hidden flex-col min-w-screen  max-w-[1440px] ">
      <div className="     h-full	flex items-center justify-center    h-full w-full">
         

          <Image src={group_1} alt=""  className="w-full h-full"/>
        </div>


       
      </div>
      <HomeSwiper/>

      <div className="min-w-screen max-w-screen pb-5 flex justify-center ">
        <div className="  grid min-[1199px]:grid-cols-4 max-[1200px]:grid-cols-2  h-[657px] max-sm:hidden max-md:hidden max-w-[1440px]  max-[500px]:px-5 min-[500px]:px-[80px] ">
          <div className="min-[1199px]:col-span-1 p-2 grid grid-rows-4 text-white  flex items-center justify-start" style={{paddingLeft:0}}>
            <div className="row-span-2 flex flex-col gap-y-2">
              <div className="w-[64px] h-[64px] bg-purple-700 rounded-2xl flex items-center justify-center " style={{backgroundColor:'#A11BC7'}}>
                <Image src={user} alt="" width={32} height={32}      quality={100}/>
              </div>
              <div className="py-2 text-xl font-bold flex " style={{fontSize:26}}>
                Chi tiết profile
              </div>
              <div className="w-[306px] text-customGrey leading-[30px]min-[1300px]::text-[30px] sm:text-[20px] max-sm:text-[12px]" style={{fontSize:20}} >
                Nếu muốn biết thêm về đối phương, lướt lên để xem trang cá nhân.
              </div>
            </div>
            <div className="row-span-2 flex flex-end flex-col gap-y-2 " style={{paddingRight:0}}>
              <div className="w-[64px] h-[64px] bg-purple-700 rounded-2xl flex items-center justify-center"  style={{backgroundColor:'#A11BC7'}}>
                <Image src={heart} alt="" width={32} height={32}     quality={100} />
              </div>
              <div className="py-2 text-xl font-bold"  style={{fontSize:26}}>Nhắn tin </div>
              <div className="w-[306px] text-sm text-customGrey leading-[30px] lg:text-[30px] sm:text-[20px] max-sm:text-[12px]" style={{fontSize:20}}>
              Dễ dàng gửi và nhận tin nhắn từ bạn bè và người thân.
              </div>
            </div>
          </div>
          <div className="min-[1199px]:col-span-2  max-[1200px]:hidden flex items-center w-full h-full justify-center">
            <Image
            
            //  width={580}
              src={group_1}
              alt=""
              key={0}
              className="max-lg:none w-full h-full max-h-[610px] max-w-[588px]"
              quality={100}
            />
          </div>
          <div className="min-[1199px]:col-span-1 p-2 grid grid-rows-4 text-white  flex items-center">
            <div className="row-span-2 flex flex-col my-10  items-end gap-y-2">
              <div className="w-[64px] h-[64px] bg-purple-700 rounded-2xl flex items-center justify-center"  style={{backgroundColor:'#A11BC7'}}>
                <Image src={reta} alt="" width={32} height={32}     quality={100}  />
              </div>
              <div className="py-2 text-xl font-bold"  style={{fontSize:26}}>Độ tương hợp</div>
              <div className="w-[306px] text-sm text-right text-customGrey leading-[30px] max-sm:leading-[22px] lg:text-[30px] sm:text-[20px] max-sm:text-[12px]" style={{fontSize:20}}>
                Khám phá mức độ tương hợp giữa bạn và đối tác.
              </div>
            </div>
            <div className="row-span-2 flex flex-col   items-end gap-y-2">
              <div className="w-[64px] h-[64px] bg-purple-700 rounded-2xl flex items-center justify-center"  style={{backgroundColor:'#A11BC7'}}>
                <Image src={location} alt="" width={32} height={32}  />
              </div>
              <div className="py-2 text-xl font-bold"  style={{fontSize:26}}>Vị trí</div>
              <div className="w-[306px] text-sm text-right text-customGrey leading-[30px] max-sm:leading-[22px] lg:text-[30px] sm:text-[20px] max-sm:text-[12px]"  style={{fontSize:20}}>
                Kết nối qua chia sẻ và gặp gỡ dễ dàng.
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
