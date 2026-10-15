#pragma once

#include <track.h>

#include <cstddef>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>

namespace mlm {

class Library {
public:
    typedef std::vector<std::shared_ptr<Track>> data_t;
    typedef std::unordered_map<std::string, std::vector<std::size_t>> name_collector_t;

    data_t& data() {
        return data_;
    }

    name_collector_t& nameIdx() {
        return name_to_idx_;
    }    

private:
    /* Iverted index model */
    data_t data_;
    name_collector_t name_to_idx_;
};

} // namespace mlm