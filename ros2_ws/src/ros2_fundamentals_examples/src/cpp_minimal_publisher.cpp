#include <cmath>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "sensor_msgs/msg/battery_state.hpp"

using namespace std::chrono_literals; // Handle time durations

class MinimalCppPublisher : public rclcpp::Node
{
public:
    MinimalCppPublisher() : Node("minimal_cpp_publisher"), count_(0), battery_level_(0.0)
    {
        publisher_ = create_publisher<std_msgs::msg::String>("/cpp_example_topic", 10);
        timer_ = create_wall_timer(500ms, std::bind(&MinimalCppPublisher::timerCallback, this));

        battery_publisher_ = create_publisher<sensor_msgs::msg::BatteryState>("/cpp_example_battery_topic", 10);
        battery_timer_ = create_wall_timer(1s, std::bind(&MinimalCppPublisher::batteryTimerCallback, this));

        RCLCPP_INFO(get_logger(), "Publishing at 2Hz");
    }

    void timerCallback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello, world! " + std::to_string(count_++);

        publisher_->publish(message);
    }

    void batteryTimerCallback()
    {
        auto message = sensor_msgs::msg::BatteryState();
        message.header.stamp = get_clock()->now();
        message.percentage = battery_level_;
        message.power_supply_status = sensor_msgs::msg::BatteryState::POWER_SUPPLY_STATUS_CHARGING;

        battery_publisher_->publish(message);

        RCLCPP_INFO(get_logger(), "Publishing battery percentage: '%.2f'", message.percentage);

        battery_level_ = std::fmod(battery_level_ + 0.01, 1.01);
    }

private:
    size_t count_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;

    double battery_level_;
    rclcpp::Publisher<sensor_msgs::msg::BatteryState>::SharedPtr battery_publisher_;
    rclcpp::TimerBase::SharedPtr battery_timer_;

};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MinimalCppPublisher>());
    rclcpp::shutdown();
    return 0;
}