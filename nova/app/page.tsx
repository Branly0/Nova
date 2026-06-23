import Image from "next/image";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="bg-blue-500 w-full h-15"></div>
      <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
        <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
          To get started, edit the page.tsx file.
        </h1>
      </div>
      <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
        <p className="max-w-xs text-lg font-medium leading-7 text-gray-600 dark:text-gray-400">
          Start by editing this file and see the changes reflected in the browser.
        </p>
      </div>
    </div>
  );
}
