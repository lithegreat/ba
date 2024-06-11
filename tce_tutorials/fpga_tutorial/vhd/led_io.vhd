-------------------------------------------------------------------------------
-- Title      : LED IO unit for TTA to be used on Altera DE2 board
-- Project    : TCE
-------------------------------------------------------------------------------
-- File       : led_io_de2.vhd
-- Author     : Otto Esko <otto.esko@tut.fi>
-- Company    : 
-- Created    : 2008-07-10
-- Last update: 2010-01-25
-- Platform   : 
-------------------------------------------------------------------------------
--
-------------------------------------------------------------------------------
-- Copyright (c) 2008
-------------------------------------------------------------------------------
-- Revisions  :
-- Date				Version		Author	Description
-- 2008-07-10		1.0     	eskoo	initial version
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
-- Entity declaration for unit led_io
-------------------------------------------------------------------------------
library IEEE;
use IEEE.Std_Logic_1164.all;
use IEEE.numeric_std.all;

entity led_io_always_1 is
	generic (
		led_count	: integer := 8); 
	port (
		-- socket interface
		t1data		:	in	std_logic_vector(led_count-1 downto 0);
		t1load		:	in	std_logic;

		-- external port interface
		led_output	: out	std_logic_vector(led_count-1 downto 0);

		-- control signals		
		glock : in std_logic;
		clk   : in std_logic;
		rstx  : in std_logic);
end led_io_always_1;


-------------------------------------------------------------------------------
-- Architecture declaration for fu_red_led_io
-------------------------------------------------------------------------------

architecture rtl of led_io_always_1 is	
	signal led_states 	: std_logic_vector(led_count-1 downto 0);
	signal control		: std_logic;
begin
	control <= t1load;
	
	regs : process (clk,rstx)
	begin -- process regs
		if rstx = '0' then
			led_states	<= (others => '0');
		elsif clk'event and clk = '1' then
			if glock = '0' then
				case control is
					when '1' =>
                      led_states	<= t1data;
					when others => null;
				end case;
			end if;
		end if;
	end process regs;
	
	led_output	<= led_states;
			
end rtl;

