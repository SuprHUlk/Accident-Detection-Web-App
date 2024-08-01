"use client";
import { SimpleChart } from "@/components/charts/SimpleChart";
import CustomChart from "@/components/charts/CustomChart";
import { useQuery } from "@tanstack/react-query";
type Props = {};

export default function Page({}: Props) {
  const {
    data: accidents,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["accidents"],
    queryFn: async () => {
      const response = await fetch("https://effective-goggles-pvg9pqr47g9frp6-8080.app.github.dev/api/v1/accident/all");
      return await response.json();
    },
  });
  return (
    <>
      {/* <SimpleChart /> */}
      <h2 className="text-xl sm:text-2xl pb-5 font-bold underline">
        Accidents Overview(Per month)
      </h2>
      {accidents?.datas && <CustomChart datas={accidents?.datas} />}
    </>
  );
}
