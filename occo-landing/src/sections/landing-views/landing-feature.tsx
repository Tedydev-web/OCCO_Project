import Image from "next/image";

////@utils
import { Content } from "@/utils";

////@assets
import Voice from "../../../public/asset/images/voice.png";
import Par from "../../../public/asset/images/parsing.png";

export default function LandingFeature() {
  return (
    <>
      <div className="pd-bottom-about py-10 lg:pt-[120px]  max-lg:px-5 sm:px-[80px] text-white 2xl:text-2xl overflow-x-scroll no-scrollbar max-[600px]:px-5 min-[600px]:px-[80px]">
        <div className="flex justify-center font-bold    max-sm:w:[240px] max-sm:min-h-[27px] sm:text-[30px] lg:text-[50px] max-sm:text-[22px] h-full">
          {" "}
          {Content.HomeContent.feature}
        </div>

        <div className="flex justify-center py-5 lg:py-10">
          <div
            className=" flex justify-center  font-medium text-center text-xl  md:w-[713px] md:min-h-[73px] pb-5  max-sm:text-[14px] sm:text-[16px] lg:text-[18px] h-full"
            style={{ color: "#817DA0" }}
          >
            {Content.HomeContent.feature_des}  <br className="max-[770px]:hidden"/> {Content.HomeContent.feature_des_a}
          </div>
        </div>

        <div className="flex justify-center">
          <div className="mg-landing max-w-[1440px] w-[1440px] flex flex-row max-sm:justify-center md:justify-center  sm:gap-x-5 sm:justify-center pb-5  max-sm:gap-x-2 overflow-x-scroll no-scrollbar   ">
         
         <div className="bg-gradient-to-r from-p_1 to-p_2 rounded-[29px] p-[1.5px] h-fit">
         <div className="lg:h-[480px] h-[517px] w-[425px]  bg-customBlack flex items-center justify-center flex-col 
             bg-customBlack rounded-[29px] max-[450px]:w-[170px] max-sm:h-[258px] max-[390px]:w-[160px]
            max-lg:h-[430px]  max-[1200px]:w-[340px] max-[800px]:w-[210px]   max-[1000px]:w-[270px] max-[700px]:max-w-[170px] flex items-center">
              <div className="w-[174px] h-[165x] max-sm:w-[78px] max-sm:h-[80px] ">
                <Image
                  src={Par}
                  className="h-[165px] max-sm:h-[80px] w-full"
                  alt=""
                  quality={100}
                />
              </div>
              <div
                style={{ color: "#7E21C8" }}
                className="font-bold text-md pt-6 pb-4 lg:text-[30px] sm:text-[20px] max-sm:text-[12px] font-[700]  "
              >
                {Content.HomeContent.paring}
              </div>
              <div className="w-full max-w-[353px] h-[75px]  text-center  lg:text-[20px] max-sm:text-[10px] sm:text-[18px]
               max-sm:h-fit max-sm:w-[151px]  leading-[34px]  max-[800px]:leading-[22px] max-sm:leading-[22px]  max-sm:text-[10px] sm:text-[16px] lg:text-[20px] px-4  ">
                {Content.HomeContent.paring_des}
              </div>
            </div>
          </div> 

           
         <div className="bg-gradient-to-r from-p_1 to-p_2 rounded-[29px] p-[1.5px] ">
         <div className="lg:h-[480px] h-[517px] w-[425px]  bg-customBlack flex items-center justify-center flex-col 
             bg-customBlack rounded-[29px] max-[450px]:w-[170px] max-sm:h-[258px] max-[390px]:w-[160px]
            max-lg:h-[430px]  max-[1200px]:w-[340px] max-[800px]:w-[210px]   max-[1000px]:w-[270px] max-[700px]:max-w-[170px]">
              <div className="w-[200px] h-[200x] max-sm:w-[78px] max-sm:h-[80px]">
                <Image
                  src={Voice}
                  className="img-landing h-[165px] max-sm:h-[80px] w-full"
                  alt=""
                  quality={100}
                />
              </div>
              <div
                style={{ color: "#7E21C8" }}
                className="font-bold text-md pt-6 pb-4   lg:text-[30px] sm:text-[20px] max-sm:text-[12px] font-[700] text-center"
              >
                {/* {Content.HomeContent.voice} */}
                {/* Phòng voice/<br className="min-[390px]:hidden"/>video call */}
                {/* <br /> */}

                Room chat
              </div>
              <div className="w-full max-w-[353px] h-[75px]  text-center  lg:text-[20px] max-sm:text-[10px] sm:text-[18px]
               max-sm:h-fit max-sm:w-[174px] leading-[34px] max-[800px]:leading-[22px] max-sm:leading-[22px]  max-sm:text-[10px] sm:text-[16px] lg:text-[20px] px-4  ">
                {Content.HomeContent.voice_des}
              </div>
          </div>
          </div> 

            {/* <div className=" h-[517px] w-[425px] 
            bg-customBlack flex items-center justify-center 
            flex-col border-2   border-fuchsia-600 bg-customBlack
             rounded-lg max-[450px]:w-[170px] max-sm:h-[258px] max-lg:h-[400px] 
             max-[1200px]:w-[310px] max-[800px]:w-[230px] ">
              <div className="w-[174px] h-[165x] max-sm:w-[78px] max-sm:h-[80px] sm:py-5 aspect-[174/165]">
                <Image
                  src={Voice}
                  className="h-full w-full"
                  alt=""
                  quality={100}
                />
              </div>
              <div
                style={{ color: "#7E21C8" }}
                className="font-bold text-md   lg:text-[30px] sm:text-[20px] max-sm:text-[12px] text-center max-sm:h-[58px] h-[72px] flex items-center"
              >
               Phòng voice / video call
              </div>
              <div className="w-full max-w-[353px] h-[75px]  text-center  lg:text-[20px] max-sm:text-[14px] sm:text-[18px]
               max-sm:h-fit max-sm:w-[151px]  leading-[34px] max-sm:leading-[22px]  max-sm:text-[10px] sm:text-[16px] lg:text-[20px] px-2 ">
                {Content.HomeContent.paring_des}
              </div>
            </div> */}
          </div>
        </div>
      </div>
    </>
  );
}
