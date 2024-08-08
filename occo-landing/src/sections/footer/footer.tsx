import Image from "next/image";
import iconPhone from "../../../public/asset/images/icon_phone.png";
import location from "../../../public/asset/images/footerLocation.png";
import mail from "../../../public/asset/images/mail.png";
export default function Footer() {
  return (
    <>
      <div className="flex justify-center text-white pb-5">
        <div className="px-5  flex flex-row max-[1180px]:flex-col max-[800px]:gap-y-3 justify-around max-w-[1440px] w-full max-lg:px-5 min-[500px]:px-[80px] ">
          <div className="w-full max-w-[180px] h-[36px] flex items-center gap-2 text-[16px] underline underline-offset-3">
            <span >
              <Image src={mail} alt=""  quality={100}      className="h-[24px] w-[30px] min-w-[30px]"/>
            </span>
            support@occo.vn
          </div>
          <div className=" w-fit min-w-[180px]  h-[36px] flex items-center gap-2 text-[16px] ">
            <span className="">
              <Image
                src={iconPhone}
                alt=""
            
                quality={100}
                     className="h-[32px] w-[28.12px] max-w-[28.12px] "
              />
            </span>
            0399961368
          </div>
          <div className=" w-fit  flex items-center gap-2 text-[16px] ">
            <span className="">
              <Image
                src={location}
                alt=""
             
              
                quality={100}
              className="h-[30px] w-[24px] min-w-[28px] "
              />
            </span>
            <div className="h-full max-h-[40px] flex items-center">
            Số 838, Ấp Vĩnh Bình, Xã An Vĩnh Ngãi, Tp Tân An, Tỉnh Long An, Việt
            Nam
            </div>
          </div>
          {/* <div className="w-full  flex items-center  h-[36px] max-sm:h-auto  text-[16px]">
            <span className="w-[40px] h-full flex items-center">
              <Image
                src={location}
                alt=""
                width={24}
                height={30}
                quality={100}
              />
            </span>
            Số 838, Ấp Vĩnh Bình, Xã An Vĩnh Ngãi, Tp Tân An, Tỉnh Long An, Việt
            Nam
          </div> */}
        </div>
      </div>
    </>
  );
}
