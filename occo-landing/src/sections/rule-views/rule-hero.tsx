import bg from "../../../public/asset/images/cc.png";
import Image from "next/image";
export default function RuleHero() {
  return (
    <>
     <div className="w-full h-full max-sm:pt-14">
     <div className="text-white overflow-x-scroll no-scrollbar   w-full bg-black grid grid-cols-3  max-lg:px-5 grid-flow-row 2xl:text-2xl px-5  lg:text-[50px] max-sm:max-h-[131px]  min-h-[512px] max-sm:min-h-[142px] " style={{backgroundImage:`url(${bg.src})`,backgroundSize:'cover',backgroundPosition:'center',backgroundRepeat:'no-repeat'}}>
        <div className="  font-bold flex items-center  
        col-span-2 w-full max-[500px]:px-5 min-[500px]:px-[80px]
         text-[46px] leading-10 max-sm:leading-5 max-lg:text-[20px] max-sm:text-[16px] sm:text-[30px] max-sm:text-[16px] text-left">
         Thỏa thuận dịch vụ
        </div>
        <div></div>
     
      </div>
     </div>
    </>
  );
}
