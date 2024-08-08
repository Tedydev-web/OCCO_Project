import group from "../../../public/asset/images/Group.png";
import Image from "next/image";
import qr1 from "../../../public/asset/images/qr1.png";
import qr2 from "../../../public/asset/images/qr2.png";
import blackAppStore from "../../../public/asset/images/blackappstore.png";
import google from "../../../public/asset/images/google_play.png";
import { Content } from "@/utils";
import email from "../../../public/asset/images/email.png";

export default function AboutFooter() {
  return (
    <>
      <div className="flex flex-col pt-20  px-10 min-w-screen  text-white justify-center relative md:hidden overflow-x-scroll overflow-x-scroll no-scrollbar ">
        <div className="flex flex-col py-5 w-full ">
          <div className="text-[50px] font-bold">
            {Content.HomeContent.registerContact}
          </div>
          <div
            className="py-3 max-sm:w-[320px] max-sm:h-[48px]  "
            style={{ color: "#817DA0" }}
          >
            {Content.HomeContent.contact_des}
          </div>
          <div className="  flex gap-5 py-3 max-sm:justify-between">
            <div className=" bg-customBlack border-b border-b-customGrey flex items-center">
              <input
                placeholder="Email của bạn"
                className="border-0 bg-customBlack  max-sm:w- focus:outline-none"
              />
            </div>

            <Image
              src={email}
              height={34}
              width={34}
              alt=""
              className="relative left-[3%]"
            />
          </div>
        </div>
        <div className=" flex justify-center z-0">
          <Image src={group} width={313} height={389} alt="" />
        </div>
        <div className=" flex justify-center relative bottom-[180px]">
          <div className="bg-gradient-to-r from-purple_cus to-blue_pur   w-[360px] h-[400px]  z-10 rounded-3xl ">
            <div className="py-10 px-5 flex flex-col">
              <div className="font-bold text-2xl">
                <div>Tải xuống ứng dụng để</div>
                <div>Kết bạn,tương tác</div>
                <div>Chia sẽ,giải trí</div>
              </div>
              <div className="py-5 flex flex-row gap-10">
                <div className="">
                  <Image src={qr1} width={70} height={70} alt="" />
                  <div className="pt-3">Appstore</div>
                </div>
                <div>
                  <Image src={qr2} width={70} height={70} alt="" />
                  <div className="pt-3">Google Play</div>
                </div>
              </div>
              <div>
                <div className="font-bold text-md">
                  Tải xuống ứng dụng ngay bây giờ để trải nghiệm
                </div>
                <div className="flex flex-row gap-5 pt-3">
                  <div>
                    <button className="  border border-white rounded-md w-[104px] h-[33px] bg-customBlack">
                      <Image src={blackAppStore} alt="" />
                    </button>
                  </div>
                  <div>
                    <button className="  border border-white rounded-md w-[104px] h-[33px] bg-customBlack">
                      <Image src={google} alt="" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-10 px-10 min-w-screen text-white max-md:hidden">
        <div className="grid grid-cols-2">
          <div className="col-span-1 row-span-2">
            {" "}
            <div className=" flex justify-center z-0">
              <Image src={group} width={313} height={389} alt="" />
            </div>
          </div>
          <div className="col-span-1 row-span-1">
            {" "}
            <div className="flex flex-col py-5 px-10">
              <div className="text-2xl font-bold">
                {Content.HomeContent.registerContact}
              </div>
              <div
                className="py-3 max-sm:w-[320px] max-sm:h-[48px]  "
                style={{ color: "#817DA0" }}
              >
                {Content.HomeContent.contact_des}
              </div>
              <div className="  flex gap-5 py-3 max-sm:justify-between">
                <div className=" bg-customBlack border-b border-b-customGrey flex items-center">
                  <input
                    placeholder="Email của bạn"
                    className="border-0 bg-customBlack max-sm:w-[270px] focus:outline-none"
                  />
                </div>

                <Image
                  src={email}
                  height={34}
                  width={34}
                  alt=""
                  className="relative left-[3%]"
                />
              </div>
            </div>
          </div>
          <div className="col-span-2 row-span-2  ">
            {" "}
            <div className=" flex justify-center relative bottom-[180px] ">
              <div className="bg-gradient-to-r from-purple_cus to-blue_pur   w-full  z-10 rounded-3xl ">
                <div className="py-10 px-5 flex flex-row items-center justify-center justify-around">
                  <div className="font-bold text-2xl">
                    <div>Tải xuống ứng dụng để</div>
                    <div>Kết bạn,tương tác</div>
                    <div>Chia sẽ,giải trí</div>
                  </div>
                  <div className="py-5 flex flex-row gap-10">
                    <div className="">
                      <Image src={qr1} width={70} height={70} alt="" />
                      <div className="pt-3">Appstore</div>
                    </div>
                    <div>
                      <Image src={qr2} width={70} height={70} alt="" />
                      <div className="pt-3">Google Play</div>
                    </div>
                  </div>
                  <div>
                    <div className="font-bold text-md">
                      Tải xuống ứng dụng ngay bây giờ để trải nghiệm
                    </div>
                    <div className="flex flex-row gap-5 pt-3">
                      <div>
                        <button className="  border border-white rounded-md w-[104px] h-[33px] bg-customBlack">
                          <Image src={blackAppStore} alt="" />
                        </button>
                      </div>
                      <div>
                        <button className="  border border-white rounded-md w-[104px] h-[33px] bg-customBlack">
                          <Image src={google} alt="" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <br />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
