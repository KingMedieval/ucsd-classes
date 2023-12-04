// CourseCatalog.js

import React, { use, useState, useEffect } from 'react';
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'] })
import Card from "../components/card"
import { ChevronDownIcon } from '@chakra-ui/icons'
import Select from 'react-select';

import {
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverHeader,
  PopoverBody,
  PopoverCloseButton,
  Button,
  PopoverFooter,
  FormControl,
  FormLabel,
  FormHelperText
} from '@chakra-ui/react'

import { subjectStyles, semesterStyles, subjects, semesterOptions, subjectOptions } from '@/lib/utils';


const CourseCatalog = () => {

  const [selectedSubjects, setSelectedSubjects] = useState([]);
  const [selectedSemesters, setSelectedSemesters] = useState([]);
  const [courses, setCourses] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [displayLanding, setDisplayLanding] = useState(true);

  function changeLanding(event) {
    setDisplayLanding(!displayLanding);
    setSearchTerm(event);
  }

  useEffect(() => {
    search();
  }, [JSON.stringify(selectedSubjects), JSON.stringify(selectedSemesters), searchTerm]);

  // This is used for focusing on proper search bar on load
  useEffect(() => {
    if (!displayLanding) {
      var input = document.getElementById('search');
    } else {
      var input = document.getElementById('landingSearch');
    }
    input.focus();
  }, [displayLanding]);

  const search = async (event) => {
    if (searchTerm.length <= 1 && selectedSubjects.length == 0 && selectedSemesters.length == 0) {
      setCourses([]);
    } else {
      const subParam = selectedSubjects.map((x) => x.value)
      const termParam = selectedSemesters.map((x) => x.value)
      const params = new URLSearchParams({ q: searchTerm, sub: subParam, term: termParam });
      fetch('/api/search?' + params)
        .then((response) => response.json())
        .then((data) => {
          setCourses(data['courses']['documents']);
        })
    }
  };


  return (
    <>
      {!displayLanding ?
        <div id="parent" className={`h-screen bg-black container mx-auto p-4 ${inter.className}`}>
          <div className='flex flex-row my-2 md:my-4 lg:my-0 lg:mt-4 lg:mb-8'>
            <img src='/favicon.ico' onClick={ () => changeLanding("") } className='my-auto w-12 h-12 md:w-20 md:h-20 lg:w-24 lg:h-24 cursor-pointer' />
            <h1 onClick={ () => changeLanding("") } className='text-2xl md:text-5xl font-semibold my-auto select-none text-white cursor-pointer'>BoilerClasses</h1>
          </div>
          {/* Search Bar */}
          <div className="mb-6">
            <input
              id="search"
              type="text"
              placeholder="Search for courses..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
              }}
              className="text-white text-xl bg-black w-full pb-2 border-b-2 focus:outline-none focus:border-blue-500 transition duration-300"
            />
          </div>
          <div className="flex flex-row mb-8 gap-5 items-center">
            <p className='mr-4 text-white whitespace-nowrap md:block hidden'>Filter by </p>
            <div className='flex flex-row w-full justify-evenly gap-5 items-center md:flex-nowrap flex-wrap'>
              <Select
                isMulti
                options={subjectOptions}
                className="basic-multi-select w-full"
                classNamePrefix="select"
                placeholder="Subject..."
                styles={subjectStyles}
                color="white"
                onChange={(value) => {
                  setSelectedSubjects(value)
                }}
              />
              <Select
                isMulti
                options={semesterOptions}
                className="basic-multi-select w-full"
                classNamePrefix="select"
                placeholder="Semester..."
                styles={semesterStyles}
                color="white"
                onChange={(value) => {
                  setSelectedSemesters(value)
                }}
              />
              <Popover placement='bottom-start'>
                <PopoverTrigger>
                  <button className='flex flex-row gap-4 px-4 py-1.5 bg-black items-center border border-gray-800 text-white rounded-xl hover:bg-black' >
                    <span>Credits</span>
                    <ChevronDownIcon color='gray-800' />
                  </button>
                </PopoverTrigger>
                <PopoverContent backgroundColor='black' borderColor='gray.800' className='bg-black border-gray-800 '>
                  <PopoverFooter borderColor='gray.800' className='flex flex-row justify-between'>
                    <Button backgroundColor='black' textColor='white' _hover={{ bg: "black" }} className='rounded-md text-white hover:bg-black' size='sm'>
                      Cancel
                    </Button>
                    <Button colorScheme='blue' size='sm'>
                      Save
                    </Button>
                  </PopoverFooter>
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="text-black grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-8">
            {courses.map(course => (
              <Card key={course.id} course={course.value} />
              // <div key={course.id}
              //   // onClick={() => openPopUp(course.title, course.subjectCode, course.courseCode, course.instructor, course.description, course.capacity, course.credits, course.term)}
              //   >


              //   {/* <a onClick={(e) => e.stopPropagation()} href={`https://www.ratemyprofessors.com/search/professors/783?q=${course.instructor[0]}`}
              //     target="_blank"
              //     rel="noopener noreferrer"
              //     className=''>
              //     <button className='bg-blue-500 text-white rounded-md px-2 py-1 shadow-md hover:-translate-y-1 transition-all bottom-0'>RateMyProfessor</button>
              //   </a> */}

            ))}
          </div>
        </div>
        :
        /* Landing Page */
        <div className="z-40 grid place-content-center mx-4 h-screen">
          <input
            id="landingSearch"
            type="text"
            placeholder="Search for courses..."
            onChange={(e) => {
              changeLanding(e.target.value);
            }}
            className="text-white text-xl bg-black w-full pb-2 border-b-2 focus:outline-none focus:border-blue-500 transition duration-300"
          />
        </div >
      }
    </>
  );
};

export default CourseCatalog;


