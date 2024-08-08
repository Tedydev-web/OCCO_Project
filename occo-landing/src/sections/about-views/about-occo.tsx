import Image from "next/image";
import double from "../../../public/asset/images/double_phone1.png";
import { Content } from "@/utils";
export default function AboutOcco() {
  return (
    <>
      <div className="min-w-screen max-w-screen   flex justify-center 2xl:text-2xl overflow-x-scroll no-scrollbar  ">
        <div className="lg:grid lg:grid-cols-2 lg:gap-5 py-5 max-[500px]:px-5 min-[500px]:px-[80px] sm:px-[80px] lg:h-[527px] min-h-fit max-lg:flex max-lg:flex-col-reverse  max-w-[1440px] ">
          <div
            className=" flex items-center  max-lg:pt-10  justify-center
        "
          >
            <div>
            <Image src={double} alt=""  className=" w-[450px] h-[400px] max-sm:w-[348px] max-sm:h-[259px] max-lg:w-[348px] max-lg:h-[259px]" quality={100}/>

            </div>
          </div>
          <div className="h-full min-h-[400px] pt-5 text-white text-justify gap-y-[20]  max-lg:text-center max-sm:h-full ">
            <div className="font-bold max-lg:text-center lg:text-[40px] sm:text-[30px] max-sm:text-[22px]">
              {Content.aboutContent.aboutOcco}
            </div>
            {Content.aboutContent.aboutOcco_des &&
              Content.aboutContent.aboutOcco_des.map((item) => {
                return (
                  <>
                    <div key={item} className="pt-5 text-customGrey lg:text-[18px] sm:text-[16px] max-sm:text-[14px]">
                      {item}
                    </div>
                  </>
                );
              })}
          </div>
        </div>
      </div>
    </>
  );
}
