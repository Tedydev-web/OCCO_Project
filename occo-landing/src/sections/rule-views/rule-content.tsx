import { Content } from "@/utils";
export default function RuleContent() {
  return (
    <>
      <div className="py-5 min-h-screen text-white flex justify-center flex flex-col overflow-x-scroll no-scrollbar  ">
      
        <div className="flex justify-center">
          <div className="max-w-[1440px] text-white max-sm:text-[14px] lg:text-[18px] max-[500px]:px-5 min-[500px]:px-[80px] ">
            {Content.rule.content.map((item, index) => {
              return (
                <>
                  <div className="" key={index}>
                    <div className="title  max-sm:text-[14px] lg:text-[18px]">
                      <b><u>{item?.title}</u></b>
                    </div>
                    <div className="mt-5 ">{item?.des}</div>
                    {item?.index.map((item, index) => {
                      return (
                        <>
                          {/* <div className="py-5 ">{item.title}</div> */}
                          {item?.title != "" ? <>

                            <div className="py-5 " dangerouslySetInnerHTML={{ __html: `${item?.title}` }} />

                          </> : <></>}
                          
                          <div>
                            {item.des.map((item, index) => {
                              return (
                                <>
                                  <div key={index} className="py-3  leading-[34px] max-sm:leading-[22px] max-sm:text-[14px] lg:text-[18px]" dangerouslySetInnerHTML={{ __html: item }} />

                                  {/* <div className="py-3  leading-[34px] max-sm:leading-[22px] max-sm:text-[14px] lg:text-[18px]">{item}</div> */}
                                </>
                              );
                            })}
                          </div>
                        </>
                      );
                    })}
                  </div>
                </>
              );
            })}
          </div>
        </div>

        <div className="flex justify-center pt-10  text-center max-sm:text-sm px-5 max-sm:text-[14px] lg:text-[18px]">
          {Content.rule.conclusion}
        </div>
      </div>
    </>
  );
}
