import { Content } from "@/utils";
import Image from "next/image";
import frame from "../../../public/asset/images/Frame.png";
export default function LandingSharing() {
  return (
    <>
      <div className="flex flex-col  justify-center text-white min-w-screen  2xl:text-2xl overflow-x-scroll no-scrollbar ">
        <div className=" flex justify-center md:flex-col">
          <div className="flex  max-sm:w-[321px] max-sm:h-[81px] font-bold text-2xl text-center sm:hidden md:hidden">
            {Content.HomeContent.share_highlight}
          </div>
          <div className="flex  max-sm:hidden max-sm:h-[81px] font-bold text-2xl text-center  justify-center text-left ">
           <div className="w-full max-w-[792px] min-h-[130px]
           text-left text-center text-[50px] max-sm:text-[22px] max-[1100px]:text-[30px] 
           flex items-center leading-[55px] max-[1100px]:leading-[40px] max-sm:w-[321px]
            max-[760px]:w-[550px] h-full  max-lg:px-5 sm:px-[80px] h-fit duration-100 lg:text-[50px] sm:text-[30px] max-sm:text-[22px]">
           Chia sẻ những khoảnh khắc và 
sự kiện trong cuộc sống của bạn
           </div>
          </div>
          

        </div>
        <div className="py-5 flex justify-center px-10  max-lg:px-5 sm:px-[80px] ">
          <div
            className="flex  max-sm:w-[353px] h-full max-sm:max-h-[242px] text-sm text-center  lg:w-[1025px] lg:h-[230px] no-scrollbar max-sm:text-[14px]
             pt-[10px] lg:text-[20px] max-sm:text-[14px] text-customGrey pb-[25px] lg:leading-[34px] max-sm:leading-[22px]  lg:text-[18px] sm:text-[16px] max-sm:text-[14px]"
            
          >
            {Content.HomeContent.highlight_des}
          </div>
        </div>
        <div className="flex justify-center pt-5">
          <div className="max-sm:hidden max-md:hidden pt-5">
          <Image src={frame} height={783} width={440} alt=""  quality={100}/>
          </div>
          <div className="md:hidden">
          <Image src={frame} height={160} width={284} alt="" quality={100} />
          </div>
        </div>
     
      </div>
    </>
  );
}
