import { Content } from "@/utils";
import benefit from "../../../public/asset/images/benefit.png";
import Image from "next/image";
import Crown from "../../../public/asset/images/crown.png";
export default function UpgradeBenefit() {
  return (
    <>
      <div className="  gap-y-5 text-white  overflow-x-scroll no-scrollbar PY-5 ">
        <div className="flex justify-center">
          <div className="max-w-[1440px] max-[500px]:px-5 min-[500px]:px-[80px] ">
            <div className="flex max-sm:justify-center pb-1 lg:text-[50px]">
              <div className="font-bold lg:text-[50px] max-sm:text-[22px] py-5" > Quyền lợi của VIP</div>
            </div>
            <div className="grid lg:grid-cols-2 max-sm:grid-cols-1  lg:justify-items-center ">
              <div className="">
                {Content.upgrade.benefit.map((item, index) => {
                  return (
                    <>
                      <div className="flex flex-row gap-5 py-1 " key={index}>
                        <div className="w-[24px] h-[24px] max-sm:w-[20px] max-sm:h-[20px] ">
                          <Image src={benefit} alt="" className="w-full h-full" />
                        </div>
                        <div className="flex items-center max-sm:text-[18px] lg:text-[20px]	" >
                          {item.title}
                        </div>
                      </div>
                    </>
                  );
                })}
              </div>
              <div className="flex justify-center  ">
                <Image
                  src={Crown}
                  loading="eager"
                  alt=""
                  className="max-lg:w-[350px] max-lg:h-[350px] lg:w-[548px] lg:h-[548px]"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
